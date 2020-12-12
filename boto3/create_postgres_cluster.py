import boto3
import json


def create_postgresql_cluster(cluster_name):

    # create a new Aurora serverless Postgresql cluster
    rds_client = boto3.client('rds')
    rds_response = rds_client.create_db_cluster(
        BackupRetentionPeriod=7,
        DatabaseName='avid',
        DBClusterIdentifier=cluster_name,
        Engine='aurora-postgresql',
        EngineVersion='10.12',
        Port=5432,
        MasterUsername='postgres',
        MasterUserPassword='hist0grm',
        StorageEncrypted=True,
        EnableIAMDatabaseAuthentication=False,
        EngineMode='serverless',
        ScalingConfiguration={
            'MinCapacity': 2,
            'MaxCapacity': 2,
            'AutoPause': False
        },
        DeletionProtection=True,
        EnableHttpEndpoint=True,
        Tags=[
            {
                'Key': 'client_id',
                'Value': 'avid'
            }
        ]
    )

    # create a new secret with postgresql database access credentials
    db_cluster = rds_response['DBCluster']
    secret_string = json.dumps({
        "username": db_cluster['MasterUsername'],
        "password": "hist0grm",
        "engine": db_cluster['Engine'],
        "host": db_cluster['Endpoint'],
        "port": db_cluster['Port'],
        "database": db_cluster['DatabaseName'],
        "dbClusterIdentifier": db_cluster['DBClusterIdentifier'],
        "dbClusterArn": db_cluster['DBClusterArn']
    })
    sm_client = boto3.client('secretsmanager')
    sm_response = sm_client.create_secret(
        Name=f'{cluster_name}-secretZ',
        Description='Credentials for accessing avid-postgresql-cluster',
        SecretString=secret_string,
        Tags=[
            {
                'Key': 'client_id',
                'Value': 'avid'
            }
        ]
    )
    print(json.dumps(sm_response, indent=2, sort_keys=False))


setup_response = {}
create_postgresql_cluster('avid-postgres-cluster')
print(json.dumps(setup_response, indent=2, sort_keys=False))
