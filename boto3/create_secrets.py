import boto3
import json

secret_string = json.dumps({
    "username": "johndoe",
    "password": "password1"
})

sm = boto3.client('secretsmanager')
response = sm.create_secret(
    Name='cool-new-secret2',
    Description='Sample Secret created via Boto3',
    SecretString=secret_string,
    Tags=[
        {
            'Key': 'org',
            'Value': 'viens.net'
        }
    ]
)

print(json.dumps(response, indent=2, sort_keys=False))
