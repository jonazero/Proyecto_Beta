from boto3 import resource
from os import getenv
from dotenv import load_dotenv

load_dotenv()
dynamodb = resource("dynamodb",
                    region_name=getenv("REGION_NAME"),
                    aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"))

tables = [
    {
        "TableName": "usuarios",
        "KeySchema": [
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'created_at',
                'KeyType': 'RANGE'
            },

        ],
        "AttributeDefinitions": [
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'created_at',
                'AttributeType': 'S'
            }
        ],
    },
]


def create_tables():
    try:
        for table in tables:
            dynamodb.create_table(
                TableName=table["TableName"],
                KeySchema=table["KeySchema"],
                AttributeDefinitions=table["AttributeDefinitions"],
                BillingMode="PAY_PER_REQUEST"
            )
    except Exception as e:
        print(e)

def add_user(id, created_at):
    table = dynamodb.Table('usuarios')
    
    response = table.put_item(
        Item={
            'id': id,
            'created_at': created_at,
            'age': 23
        }
    )
    
    return response

add_user('1', "5/7/1991")