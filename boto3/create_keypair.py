import boto3
import os


def create_keypair(prefix):
    keypair_name = f'{prefix}-keypair'

    ec2 = boto3.resource('ec2')
    filename = f'{keypair_name}.pem'
    outfile = open(filename, 'w')
    key_pair = ec2.create_key_pair(KeyName=keypair_name)
    KeyPairOut = str(key_pair.key_material)
    outfile.write(KeyPairOut)

    # chmod 400 ec2-keypair.pem
    shell_command = f'chmod 400 {filename}'
    os.system(shell_command)


create_keypair('viens')
