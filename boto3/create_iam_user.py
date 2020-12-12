import boto3
import json, string, random
from botocore.exceptions import ClientError

iam_client = boto3.client('iam')

