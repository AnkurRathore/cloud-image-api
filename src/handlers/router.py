import json
import logging
from src.handlers.upload import handle_upload

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Main entry point for API Gateway Proxy Integration."""
    http_method = event.get("httpMethod")
    resource = event.get("resource", "")

    if http_method == "POST" and resource == "/images":
        return handle_upload(event, context)
    
        
    return {
        "statusCode": 404,
        "body": json.dumps({"error": f"Route not found: {http_method} {resource}"})
    }