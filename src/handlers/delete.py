import json
import logging
from botocore.exceptions import ClientError
from src.utils.aws import get_s3_client, get_dynamodb_resource
from src.utils.config import BUCKET_NAME, TABLE_NAME

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = get_s3_client()
dynamodb = get_dynamodb_resource()
table = dynamodb.Table(TABLE_NAME)

def handle_delete(event, context):
    """
    DELETE /images/{id}
    Deletes the image from S3 and removes its metadata from DynamoDB.
    """
    try:
        path_params = event.get("pathParameters") or {}
        image_id = path_params.get("id")

        if not image_id:
            return _build_response(400, {"error": "Missing image_id in path parameters"})

        # 1. Fetch metadata to get the s3_key
        logger.info(f"Fetching metadata for deletion: {image_id}")
        response = table.get_item(Key={"image_id": image_id})
        item = response.get("Item")

        if not item:
            return _build_response(404, {"error": f"Image with ID {image_id} not found"})

        s3_key = item.get("s3_key")

        # 2. Delete binary from S3
        logger.info(f"Deleting object from S3: {s3_key}")
        try:
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
        except ClientError as e:
            logger.error(f"Failed to delete S3 object: {str(e)}")
            

        # 3. Delete metadata from DynamoDB
        logger.info(f"Deleting metadata from DynamoDB: {image_id}")
        table.delete_item(Key={"image_id": image_id})

        return _build_response(200, {
            "message": f"Image {image_id} successfully deleted."
        })

    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        return _build_response(500, {"error": "Internal server error"})


def _build_response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }