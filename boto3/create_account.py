import boto3

account_name = 'ACME @ ViensLLC'
client_id = 'acme'

account_email = f'{client_id}@viens.net'
resource_tag = {
    'Key': 'client_id',
    'Value': client_id
}

client = boto3.client('organizations')
response = client.create_account(
    Email=account_email,
    AccountName=account_name,
    Tags=[resource_tag]
)

