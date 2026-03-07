import json
import os

# Ensure Boto3 knows to talk to LocalStack
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["ENDPOINT_URL"] = "http://localhost:4566"

from src.handlers.router import lambda_handler



# Mock the API Gateway Event with query parameters
mock_api_gateway_event = {
    "httpMethod": "GET",
    "resource": "/images",
    "queryStringParameters": {
        "user_id": "ankur_123"  # This matches the user we uploaded yesterday!
    }
}

print("Invoking GET /images ...")
response = lambda_handler(mock_api_gateway_event, context=None)

print("\n--- LAMBDA RESPONSE ---")
print(f"Status Code: {response['statusCode']}")
print(f"Body: {json.dumps(json.loads(response['body']), indent=2)}")