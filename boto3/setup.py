import boto3
import json


def create_jumpbox(prefix, image_id):
    jumpbox_name = f'{prefix}-jumpbox'
    jumpbox_kp_name = f'{prefix}-keypair'
    jumpbox_sg_name = f'{jumpbox_name}-sg'

    # Create security group
    ec2 = boto3.resource('ec2')
    jumpbox_sg = ec2.create_security_group(
        GroupName=jumpbox_sg_name,
        Description='Allows SSH access to ec2 jumpbox instance',
        VpcId=__get_default_vpc_id()
    )

    # Add an inbound rule to the security group for SSH access to jumpbox
    jumpbox_sg.authorize_ingress(
        DryRun=False,
        IpPermissions=[
            {
                'FromPort': 22,
                'ToPort': 22,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Allows SSH access to ec2 jumpbox instance'
                    }
                ]
            }
        ]
    )

    # Tag the security group
    jumpbox_sg.create_tags(
        Tags=[
            {
                'Key': 'Name',
                'Value': jumpbox_sg_name
            }
        ]
    )

    # Create the jumpbox
    instances = ec2.create_instances(
        ImageId=image_id,
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=jumpbox_kp_name,
        Monitoring={
            'Enabled': False
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': jumpbox_name
                    }
                ]
            }
        ],
        SecurityGroupIds=[
            jumpbox_sg.id,
        ]
    )

    # Add an inbound rule to the default security group to access PostgreSQL
    ec2_client = boto3.client('ec2')
    ec2_response = ec2_client.authorize_security_group_ingress(
        GroupId=__get_default_security_group_id(),
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 5432,
                'ToPort': 5432,
                'UserIdGroupPairs': [
                    {
                        'GroupId': jumpbox_sg.id,
                        'Description': 'Allows SSH access to PostgreSQL database cluster'
                    }
                ]
            }
        ]
    )


def create_postgresql_cluster(prefix, username, password):
    cluster_name = f'{prefix}-postgres-cluster'

    # create a new Aurora serverless Postgresql cluster
    rds_client = boto3.client('rds')
    rds_response = rds_client.create_db_cluster(
        BackupRetentionPeriod=7,
        DatabaseName=prefix,
        DBClusterIdentifier=cluster_name,
        Engine='aurora-postgresql',
        EngineVersion='10.12',
        Port=5432,
        MasterUsername=username,
        MasterUserPassword=password,
        StorageEncrypted=True,
        EnableIAMDatabaseAuthentication=False,
        EngineMode='serverless',
        ScalingConfiguration={
            'MinCapacity': 2,
            'MaxCapacity': 2,
            'AutoPause': False
        },
        DeletionProtection=True,
        EnableHttpEndpoint=True
    )

    # create a new secret with postgresql database access credentials
    db_cluster = rds_response['DBCluster']
    secret_string = json.dumps({
        "username": db_cluster['MasterUsername'],
        "password": password,
        "engine": db_cluster['Engine'],
        "host": db_cluster['Endpoint'],
        "port": db_cluster['Port'],
        "database": db_cluster['DatabaseName'],
        "dbClusterIdentifier": db_cluster['DBClusterIdentifier'],
        "dbClusterArn": db_cluster['DBClusterArn']
    })
    sm_client = boto3.client('secretsmanager')
    sm_response = sm_client.create_secret(
        Name=f'{cluster_name}-secret',
        Description=f'Credentials for accessing {cluster_name}',
        SecretString=secret_string
    )
    print(json.dumps(sm_response, indent=2, sort_keys=False))


def create_ecs_cluster(prefix, region):
    cluster_name = f'{prefix}-ecs-cluster'
    exe_role_name = f'{prefix}-ecs-task-execution-role'
    task_sg_name = f'{prefix}-ecs-task-sg'
    task_sg_desc = 'Allows ECS task execution access to containers from ECR'

    # Create ecs cluster
    ecs_client = boto3.client('ecs')
    ecs_cluster = ecs_client.create_cluster(
        clusterName=cluster_name,
        tags=[
            {
                'key': 'Name',
                'value': cluster_name
            }
        ]
    )

    # Create ecs task execution role
    iam_client = boto3.client('iam')
    ecs_role = iam_client.create_role(
        RoleName=exe_role_name,
        AssumeRolePolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }),
        Description='Allows ECS tasks to call AWS services on your behalf.',
        Tags=[
            {
                'Key': 'Name',
                'Value': exe_role_name
            }
        ]
    )
    response = iam_client.attach_role_policy(
        RoleName=exe_role_name,
        PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
    )

    # Create ECS task security group
    ec2_resource = boto3.resource('ec2')
    ecs_sg = ec2_resource.create_security_group(   # create new security group
        GroupName=task_sg_name,
        Description=task_sg_desc,
        VpcId=__get_default_vpc_id()
    )
    ecs_sg.authorize_ingress(   # add an inbound rule to the security group
        DryRun=False,
        IpPermissions=[
            {
                'FromPort': 80,
                'ToPort': 80,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': task_sg_desc
                    }
                ]
            }
        ]
    )
    ecs_sg.create_tags(   # add Name tag to the security group
        Tags=[
            {
                'Key': 'Name',
                'Value': task_sg_name
            }
        ]
    )


def register_ecs_task_definition(ecs_td_name, ecr_name):
    account_id = __get_aws_account_id()
    ecs_td_role_arn = f'arn:aws:iam::{account_id}:role/{ecs_td_name}'

    ecs_client = boto3.client('ecs')
    response = ecs_client.register_task_definition(     # Create an ecs task definition
        family=ecs_td_name,
        taskRoleArn=ecs_td_role_arn,
        executionRoleArn=ecs_td_role_arn,
        cpu='256',
        memory='512',
        networkMode='awsvpc',
        requiresCompatibilities=[
            'FARGATE'
        ],
        containerDefinitions=[
            {
                'name': ecs_td_name,
                'image': ecr_name,
                'cpu': 256,
                'memory': 512,
                'memoryReservation': 128,
                'essential': True
            }
        ],
    )


def __get_aws_account_id():
    sts_client = boto3.client("sts")
    account_id = sts_client.get_caller_identity()["Account"]
    return account_id


def __get_default_vpc_id():
    # get the vpc ID of the 'default' VPC
    ec2_client = boto3.client('ec2')
    ec2_response = ec2_client.describe_vpcs(
        Filters=[
            dict(Name='isDefault', Values=['true'])
        ]
    )
    vpc_list = ec2_response['Vpcs']
    default_vpc = vpc_list[0]
    return default_vpc['VpcId']


def __get_default_security_group_id():
    # get the group ID of the 'default' security group
    ec2_client = boto3.client('ec2')
    ec2_response = ec2_client.describe_security_groups(
        Filters=[
            dict(Name='group-name', Values=['default'])
        ]
    )
    default_sg = ec2_response['SecurityGroups'][0]
    return default_sg['GroupId']


create_jumpbox('avid', 'ami-04d29b6f966df1537')  # us-east-2 = ami-09558250a3419e7d0
#create_postgresql_cluster('avid', 'postgres', 'hist0grm')
#create_ecs_cluster('avid')

#register_ecs_task_definition('avid-ingest-ecs-td', '677126791323.dkr.ecr.us-east-1.amazonaws.com/avid-ingest:latest')
