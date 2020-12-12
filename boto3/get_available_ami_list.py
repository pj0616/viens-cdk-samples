import json
import boto3

ec2_client = boto3.client('ec2', region_name='us-east-1')

#images = ec2_client.describe_images(Owners=['self'])
#images = ec2_client.describe_images(Owners=['137112412989'])
images = ec2_client.describe_images(ImageIds=['ami-04bf6dcdc9ab498ca'])
#images = ec2_client.describe_images()

print(json.dumps(images, indent=2, sort_keys=False))

#print(images)
