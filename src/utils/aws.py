import boto3
from src.utils.config import AWS_REGION, AWS_ENDPOINT_URL

def get_s3_client():
    if AWS_ENDPOINT_URL:
        return boto3.client('s3', region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT_URL)
    return boto3.client('s3', region_name=AWS_REGION)

def get_dynamodb_resource():
    if AWS_ENDPOINT_URL:
        return boto3.resource('dynamodb', region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT_URL)
    return boto3.resource('dynamodb', region_name=AWS_REGION)