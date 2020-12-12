import boto3

client_id = 'acme'
domain = 'viens.net'

client_table_name = f'client.{domain}'
product_table_name = f'product.{domain}'
provider_table_name = f'provider.{domain}'
source_table_name = f'source.{domain}'

resource_tag = {
    'Key': 'client_id',
    'Value': client_id
}


dynamodb = boto3.client('dynamodb')


#
def create_table(table_name, key_name, tag):

    client_table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': key_name,
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': key_name,
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        },
        Tags=[tag]
    )


# create a client table
create_table(client_table_name, 'client_id', resource_tag)
create_table(provider_table_name, 'provider_id', resource_tag)
create_table(product_table_name, 'product_id', resource_tag)
create_table(source_table_name, 'source_key', resource_tag)

