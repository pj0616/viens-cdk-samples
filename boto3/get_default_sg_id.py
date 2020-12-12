import boto3


def get_default_security_group_id():
    # get the group ID of the 'default' security group
    ec2_client = boto3.client('ec2')
    ec2_response = ec2_client.describe_security_groups(
        Filters=[
            dict(Name='group-name', Values=['default'])
        ]
    )
    default_sg = ec2_response['SecurityGroups'][0]
    return default_sg['GroupId']


dsg_id = get_default_security_group_id()
print('Security Group Id = {}'.format(dsg_id))
