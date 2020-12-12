import boto3


def get_default_vpc_id():
    # get the Vpc ID of the 'default' Vpc
    ec2_client = boto3.client('ec2')
    ec2_response = ec2_client.describe_vpcs(
        Filters=[
            dict(Name='isDefault', Values=['true'])
        ]
    )
    vpc_list = ec2_response['Vpcs']
    default_vpc = vpc_list[0]
    return default_vpc['VpcId']


vpc_id = get_default_vpc_id()
print('VPC Id = {}'.format(vpc_id))