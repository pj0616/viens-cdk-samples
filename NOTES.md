In a terminal winfow execute the following unix commands:

    mkdir project-name
    cd project-name
    cdk init app --language python
    pip install --upgrade pip
    source .venv/bin/activate

Edit the setup.py file in the project root directory setting the aws-cdk.core version to 1.76.0

    install_requires=[
        "aws-cdk.core==1.76.0",
    ],
    
Replace the contents of requirements.txt with the following:

    aws-cdk.core
    aws-cdk.aws-s3
    aws-cdk.aws-ec2
    aws-cdk.aws-iam
    aws-cdk.aws-rds
    aws-cdk.aws-ecs

Add the neccessary aws cdk python modules to the project:

    python -m pip install -r requirements.txt


You can get the default vpc ID using the AWS CLI with the following:

  # The ID of the default VPC can be obtained using the following AWS CLI command:
  aws ec2 describe-vpcs \
    --filters Name=isDefault,Values=true \
    --query 'Vpcs[*].VpcId' \
    --output text


You can get the default security group ID using the AWS CLI with the following:

  # The ID of the default Security Group can be obtained using the following AWS CLI command:
  aws ec2 describe-security-groups \
    --filters Name=group-name,Values=default \
    --query 'SecurityGroups[*].GroupId' \
    --output text
