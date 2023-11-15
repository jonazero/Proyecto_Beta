from decimal import Decimal
from typing import List
from .db import dynamodb
from botocore.exceptions import ClientError
from fastapi.responses import JSONResponse
from boto3.dynamodb.conditions import Key
from models.user import User, UserData, ArrayRequest
import json
table = dynamodb.Table("users")


def create_user(user: dict):
    try:
        table.put_item(Item=user)
        return user
    except ClientError as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


def get_by_id(id: str):
    try:
        response = table.query(
            KeyConditionExpression=Key("id").eq(id)
        )
        return response["Items"]
    except ClientError as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


def get_by_email(email: str):
    try:
        response = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email)
        )
        if response["Items"]:
            return response["Items"][0]
    except ClientError as e:
        print(e)
        return JSONResponse(content=e.response["Error"], status_code=500)


def get_users():
    try:
        response = table.scan(
            Limit=5,
            AttributesToGet=["username", "id"]
        )
        return response["Items"]
    except ClientError as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


def delete_user(user: dict):
    try:
        response = table.delete_item(
            Key={
                "id": user["id"],
                "created_at": user["created_at"]
            }
        )
        return response
    except ClientError as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


def update_user(keyData: List[ArrayRequest], user: User):
    json_data = [dict(obj) for obj in keyData]
    for obj in json_data:
        if obj["coords"] is not None:
            obj["coords"] = [Decimal(obj["coords"][0]), Decimal(obj["coords"][1])]
    try:
        response = table.update_item(
            Key={
                "id": user.id,
                "created_at": user.created_at
            },
            UpdateExpression="SET keyData = list_append(keyData, :keyData)",
            #UpdateExpression="SET keyData = :keyData",
            ExpressionAttributeValues={
                ":keyData": json_data,
            }
        )
        return response
    except ClientError as e:
        return JSONResponse(content=e.response["Error"], status_code=500)
