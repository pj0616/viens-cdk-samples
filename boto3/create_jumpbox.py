# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Subnet.create_instances

import boto3

account_name = 'ACME @ ViensLLC'
account_email = 'acme@viens.net'
client_id = 'acme'

key_name = f'{client_id}_ec2_keypair'
keypair_filename = f'{key_name}.pem'

image_id = 'ami-04bf6dcdc9ab498ca'
instance_type = 't2.micro'
instance_name = f'{client_id} Bastion'

ec2 = boto3.resource('ec2')

# create a new EC2 instance
instances = ec2.create_instances(
     ImageId=image_id,
     MinCount=1,
     MaxCount=1,
     InstanceType=instance_type,
     KeyName=key_name,
     TagSpecifications=[
          {
               'ResourceType': 'instance',
               'Tags': [
                    {
                         'Key': 'Name',
                         'Value': instance_name
                    }
               ]
          }
     ]
)
