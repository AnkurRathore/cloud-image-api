import json
import logging
from boto3.dynamodb.conditions import Key
from src.utils.aws import get_dynamodb_resource
from src.utils.config import TABLE_NAME

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = get_dynamodb_resource()
table = dynamodb.Table(TABLE_NAME)

def handle_list(event, context):
    """
    GET /images
    Supports query parameters: ?user_id=ankur_123 & tag=travel
    """
    try:
        # API Gateway passes query strings here
        query_params = event.get("queryStringParameters") or {}
        user_id = query_params.get("user_id")
        tag = query_params.get("tag")

        if user_id:
            
            logger.info(f"Querying UserIdIndex for user_id: {user_id}")
            response = table.query(
                IndexName="UserIdIndex",
                KeyConditionExpression=Key("user_id").eq(user_id)
            )
            items = response.get("Items",[])
        else:
            # Fallback: If no user_id is provided, scan the table.
            
            logger.info("No user_id provided. Scanning entire table.")
            response = table.scan()
            items = response.get("Items",[])

        # Filter #2: Filter by tag (if provided)
        if tag:
            items =[item for item in items if tag in item.get("tags", [])]

        return _build_response(200, {
            "count": len(items),
            "images": items
        })

    except Exception as e:
        logger.error(f"Error listing images: {str(e)}")
        return _build_response(500, {"error": "Internal server error"})


def _build_response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }