import json

from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    core
)
from aws_cdk.aws_rds import CfnDBCluster, CfnDBClusterProps
from aws_cdk.core import App, Stack, Tags, Environment


class AvidJumpboxStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, env=Environment(account="677126791323", region="us-east-1"), **kwargs)

        # Get a reference to the default VPC
        avid_default_vpc = ec2.Vpc.from_lookup(
            self,
            id="DefaultVPC",
            is_default=True)

        # Create jumpbox security group
        avid_jumpbox_sg = ec2.SecurityGroup(
            self,
            id='JumpboxSG',
            vpc=avid_default_vpc,
            allow_all_outbound=True,
            description='Allows SSH access to ec2 jumpbox instance',
            security_group_name='avid-jumpbox-sg')

        # Add an inbound rule to the security group for SSH access to jumpbox
        avid_jumpbox_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description='Allows SSH access to ec2 jumpbox instance')

        # Populate the security group Name column in the web console by tagging
        Tags.of(avid_jumpbox_sg).add('Name', 'avid-jumpbox-sg')

        # Construct the jumpbox EC2 AMI
        amazon_linux_image = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE)

        # Create the jumpbox EC2 instance
        avid_jumpbox = ec2.Instance(
            self,
            id='Jumpbox',
            instance_type=ec2.InstanceType('t2.micro'),
            machine_image=amazon_linux_image,
            vpc=avid_default_vpc,
            instance_name='avid-jumpbox',
            key_name='avid-keypair',
            security_group=avid_jumpbox_sg)

        # Populate the ec2 instance Name column in the web console by tagging
        Tags.of(avid_jumpbox).add('Name', 'avid-jumpbox')

        # Get a reference to the default security group
        avid_default_sg = ec2.SecurityGroup.from_security_group_id(
            self,
            id='DefaultSG',
            security_group_id='sg-f106ad87')

        # Add an inbound rule to the default vpc's default security group for SSH access to postgreSQL
        avid_default_sg.add_ingress_rule(
            peer=avid_jumpbox_sg,
            connection=ec2.Port.tcp(5432),
            description='Allows SSH access to PostgreSQL database cluster1')

        # Load dictionary with db cluster properties
        db_props = {
            'engine': 'aurora-postgresql',
            'engine_version': '10.12',
            'engine_mode': 'serverless',
            'db_name': 'avid',
            'db_cluster_identifier': 'avid-postgres-cluster',
            'deletion_protection': False,
            'enable_http_endpoint': True,
            'enable_iam_database_authentication': False,
            'db_master_username': 'postgres',
            'db_master_password': 'hist0grm',
            'port': 5432,
            'storage_encrypted': True
        }

        #
        db_cluster = CfnDBCluster(
            self,
            id='avid-postgres-cluster',
            engine=db_props['engine'],
            engine_version=db_props['engine_version'],
            engine_mode=db_props['engine_mode'],
            database_name=db_props['db_name'],
            db_cluster_identifier=db_props['db_cluster_identifier'],
            deletion_protection=db_props['deletion_protection'],
            enable_http_endpoint=db_props['enable_http_endpoint'],
            enable_iam_database_authentication=db_props['enable_iam_database_authentication'],
            master_username=db_props['db_master_username'],
            master_user_password=db_props['db_master_password'],
            port=db_props['port'],
            scaling_configuration=CfnDBCluster.ScalingConfigurationProperty(
                auto_pause=False,
                min_capacity=2,
                max_capacity=2,
                seconds_until_auto_pause=300  # 5 minutes
            ),
            storage_encrypted=db_props['storage_encrypted']
        )


