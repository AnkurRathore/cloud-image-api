import json
import uuid
import logging
from datetime import datetime, timezone

from src.utils.aws import get_s3_client, get_dynamodb_resource
from src.utils.config import BUCKET_NAME, TABLE_NAME, PRESIGNED_URL_EXPIRATION

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = get_s3_client()
dynamodb = get_dynamodb_resource()
table = dynamodb.Table(TABLE_NAME)

def handle_upload(event, context):
    """
    POST /images
    Expected Body: {"user_id": "user123", "filename": "vacation.jpg"}
    """
    try:
        # 1. Parse Input
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")
        filename = body.get("filename")
        
        if not user_id or not filename:
            return _build_response(400, {"error": "Missing 'user_id' or 'filename'"})

        # 2. Generate IDs
        image_id = str(uuid.uuid4())
        upload_date = datetime.now(timezone.utc).isoformat()
        s3_key = f"{user_id}/{image_id}_{filename}"

        # 3. Generate S3 Presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key, 'ContentType': 'image/jpeg'},
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )

        # 4. Save Metadata to DynamoDB
        metadata_item = {
            "image_id": image_id,
            "user_id": user_id,
            "upload_date": upload_date,
            "s3_key": s3_key,
            "filename": filename,
            "status": "pending_upload" 
        }
        
        table.put_item(Item=metadata_item)
        logger.info(f"Metadata saved for image_id: {image_id}")

        # 5. Return Response
        return _build_response(201, {
            "message": "Metadata created. Use 'upload_url' to PUT the image binary.",
            "image_id": image_id,
            "upload_url": presigned_url,
            "metadata": metadata_item
        })

    except json.JSONDecodeError:
        return _build_response(400, {"error": "Invalid JSON payload"})
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        return _build_response(500, {"error": "Internal server error"})


def _build_response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }