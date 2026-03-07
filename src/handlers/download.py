import json
import logging
from src.utils.aws import get_s3_client, get_dynamodb_resource
from src.utils.config import BUCKET_NAME, TABLE_NAME, PRESIGNED_URL_EXPIRATION

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = get_s3_client()
dynamodb = get_dynamodb_resource()
table = dynamodb.Table(TABLE_NAME)

def handle_download(event, context):
    """
    GET /images/{id}
    Returns image metadata and a short-lived S3 Presigned URL to view/download the image.
    """
    try:
        # 1. Extract image_id from API Gateway path parameters
        path_params = event.get("pathParameters") or {}
        image_id = path_params.get("id")

        if not image_id:
            return _build_response(400, {"error": "Missing image_id in path parameters"})

        # 2. Fetch metadata from DynamoDB
        logger.info(f"Fetching metadata for image_id: {image_id}")
        response = table.get_item(Key={"image_id": image_id})
        item = response.get("Item")

        if not item:
            return _build_response(404, {"error": f"Image with ID {image_id} not found"})

        # 3. Generate S3 Presigned GET URL
        s3_key = item.get("s3_key")
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )

        # 4. Return metadata + secure download link
        return _build_response(200, {
            "image_id": image_id,
            "metadata": item,
            "download_url": download_url
        })

    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        return _build_response(500, {"error": "Internal server error"})


def _build_response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }