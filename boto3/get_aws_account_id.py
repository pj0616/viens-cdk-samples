import boto3


def get_aws_account_id():
    sts_client = boto3.client("sts")
    return sts_client.get_caller_identity()["Account"]


account_id = get_aws_account_id()
print('AWS Account ID = {}'.format(account_id))