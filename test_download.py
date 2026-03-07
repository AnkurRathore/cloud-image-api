import json
import os

# 1. SET CREDENTIALS FIRST!
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["ENDPOINT_URL"] = "http://localhost:4566"

from src.handlers.router import lambda_handler


TEST_IMAGE_ID = "1d9f1a0e-5121-4a59-86f8-3a55dd7eb1f3" 

# Mock the API Gateway Event with path parameters
mock_api_gateway_event = {
    "httpMethod": "GET",
    "resource": "/images/{id}",
    "pathParameters": {
        "id": TEST_IMAGE_ID
    }
}

print(f"Invoking GET /images/{TEST_IMAGE_ID} ...")
response = lambda_handler(mock_api_gateway_event, context=None)

print("\n--- LAMBDA RESPONSE ---")
print(f"Status Code: {response['statusCode']}")
print(f"Body: {json.dumps(json.loads(response['body']), indent=2)}")