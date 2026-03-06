import os

# AWS Configurations
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
# If running locally, this will be http://localhost:4566
AWS_ENDPOINT_URL = os.getenv("ENDPOINT_URL", "http://localhost:4566")

# Resource Names
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "image-service-bucket")
TABLE_NAME = os.getenv("DYNAMO_TABLE", "images")

# Presigned URL expiration in seconds
PRESIGNED_URL_EXPIRATION = 3600