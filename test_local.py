import json
from src.handlers.router import lambda_handler

# 1. Mock the API Gateway Event
mock_api_gateway_event = {
    "httpMethod": "POST",
    "resource": "/images",
    "body": json.dumps({
        "user_id": "ankur_123",
        "filename": "my_resume.pdf",
        "tags": ["document", "important"]
    })
}

# 2. Calling Lambda function locally
print("Invoking Lambda Handler...")
response = lambda_handler(mock_api_gateway_event, context=None)

# 3. Print the result!
print("\n--- LAMBDA RESPONSE ---")
print(f"Status Code: {response['statusCode']}")
print(f"Body: {json.dumps(json.loads(response['body']), indent=2)}")