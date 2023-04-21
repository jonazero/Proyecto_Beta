from boto3 import resource
from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL.format(
        user=getenv("AWS_MYSQL_USERNAME"),
        password=getenv("AWS_MYSQL_PWD"),
        host=getenv("AWS_MYSQL_HOST"),
        port="3306",
        database=getenv("AWS_MYSQL_DB"),
    )
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


dynamodb = resource("dynamodb",
                    aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=getenv("REGION_NAME"))


tables = [
    {
        "TableName": "users",
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
