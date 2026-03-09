import os
import json
import pytest
import boto3
from moto import mock_aws

# 1. SET ENV VARS FIRST
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["S3_BUCKET_NAME"] = "test-bucket"
os.environ["DYNAMO_TABLE"] = "test-table"

# CRITICAL FIX: Ensure Boto3 doesn't try to use LocalStack during unit tests
if "ENDPOINT_URL" in os.environ:
    del os.environ["ENDPOINT_URL"]

# 2. START THE MOCK ENGINE GLOBALLY 
mock = mock_aws()
mock.start()

# 3. NOW IMPORT THE APP
from src.handlers.router import lambda_handler

# 4. CREATE THE MOCK INFRASTRUCTURE
s3 = boto3.client("s3", region_name="us-east-1")
s3.create_bucket(Bucket="test-bucket")

dynamodb = boto3.client("dynamodb", region_name="us-east-1")
dynamodb.create_table(
    TableName="test-table",
    KeySchema=[{"AttributeName": "image_id", "KeyType": "HASH"}],
    AttributeDefinitions=[
        {"AttributeName": "image_id", "AttributeType": "S"},
        {"AttributeName": "user_id", "AttributeType": "S"}
    ],
    GlobalSecondaryIndexes=[{
        "IndexName": "UserIdIndex",
        "KeySchema":[{"AttributeName": "user_id", "KeyType": "HASH"}],
        "Projection": {"ProjectionType": "ALL"}
    }],
    BillingMode="PAY_PER_REQUEST"
)

# 5. THE TESTS
def test_upload_image():
    event = {
        "httpMethod": "POST",
        "resource": "/images",
        "body": json.dumps({"user_id": "test_user", "filename": "photo.png", "tags": ["art"]})
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert "upload_url" in body

def test_list_images():
    post_event = {
        "httpMethod": "POST",
        "resource": "/images",
        "body": json.dumps({"user_id": "user1", "filename": "a.png"})
    }
    lambda_handler(post_event, None)

    get_event = {
        "httpMethod": "GET",
        "resource": "/images",
        "queryStringParameters": {"user_id": "user1"}
    }
    response = lambda_handler(get_event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["count"] == 1

def test_download_image_not_found():
    event = {
        "httpMethod": "GET",
        "resource": "/images/{id}",
        "pathParameters": {"id": "fake-id"}
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 404

def test_delete_image_not_found():
    event = {
        "httpMethod": "DELETE",
        "resource": "/images/{id}",
        "pathParameters": {"id": "fake-id"}
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 404