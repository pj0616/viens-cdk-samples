import boto3

client_id = 'acme'
bucket_name = f'{client_id}.viens.net'

s3 = boto3.resource('s3')

# create a new EC2 instance
bucket = s3.create_bucket(
    Bucket=bucket_name
)
