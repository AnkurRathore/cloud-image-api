import json
import logging
from src.handlers.upload import handle_upload
from src.handlers.list import handle_list
from src.handlers.download import handle_download
from src.handlers.delete import handle_delete

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Main entry point for API Gateway Proxy Integration."""
    http_method = event.get("httpMethod")
    resource = event.get("resource", "")

    if http_method == "POST" and resource == "/images":
        return handle_upload(event, context)
    
    elif http_method == "GET" and resource == "/images":
        return handle_list(event, context)
    
    elif http_method == "GET" and resource == "/images/{id}":
        return handle_download(event, context)

    elif http_method == "DELETE" and resource == "/images/{id}":
        return handle_delete(event, context)
       
    return {
        "statusCode": 404,
        "body": json.dumps({"error": f"Route not found: {http_method} {resource}"})
    }