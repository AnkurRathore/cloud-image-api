

# Cloud Image Service API

A scalable, serverless image upload and metadata storage service built for AWS. This project simulates an Instagram-like backend, utilizing **API Gateway, AWS Lambda, Amazon S3, and Amazon DynamoDB**, running entirely locally via **LocalStack**.

## Architectural Decisions

As a Lead Platform Engineer, ensuring the system is scalable, cost-effective, and secure is paramount. Here are the key design decisions made for this service:

### 1. S3 Pre-signed URLs for Image Uploads
**The Problem:** Amazon API Gateway has a hard payload limit of 10MB, and processing binary image data directly through AWS Lambda is memory-intensive, slow, and expensive.
**The Solution:** The `POST /images` endpoint does not accept image binaries. Instead, it accepts JSON metadata, persists it to DynamoDB, and generates an **S3 Pre-signed POST URL**. The client then uses this temporary, secure URL to upload the binary directly to S3. This completely bypasses the API Gateway bottleneck, keeping Lambda execution times under 100ms and allowing for theoretically infinite scalability.

### 2. DynamoDB Global Secondary Indexes (GSIs)
**The Problem:** The requirements specify filtering images by at least two parameters (e.g., `user_id` and `upload_date`). Performing a full table `Scan` in DynamoDB is highly inefficient and expensive at scale.
**The Solution:** The DynamoDB table is designed with a primary `HASH` key of `image_id`. To support efficient $O(\log N)$ filtering, two Global Secondary Indexes (GSIs) are provisioned: `UserIdIndex` and `UploadDateIndex`. This allows the `GET /images` endpoint to use efficient `Query` operations instead of `Scans`.

### 3. Proxy Routing Pattern (Fat Lambda)
For ease of local development and deployment in this exercise, the API utilizes a Lambda Proxy Integration pattern. A single Lambda function acts as the router (`src/handlers/router.py`), delegating business logic to specific controller modules. 


## Quick Start (Local Development)

### Prerequisites
* [Docker](https://docs.docker.com/get-docker/) & Docker Compose
* [AWS CLI](https://aws.amazon.com/cli/) (or `awslocal`)
* Python 3.7+

### 1. Start LocalStack
Spin up the local AWS environment (S3, DynamoDB, API Gateway, Lambda):
```bash
docker-compose up -d
```
*Wait a few seconds for the container to become healthy.*

### 2. Bootstrap AWS Resources
Run the initialization script to automatically create the S3 bucket and DynamoDB table inside LocalStack:
```bash
chmod +x ./infra/bootstrap.sh
./infra/bootstrap.sh
```

### 3. Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run Local Invocation Test
Verify the Lambda handler works locally:
```bash
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_DEFAULT_REGION="us-east-1"
export ENDPOINT_URL="http://localhost:4566"

python test_local.py
```

---

## API Documentation

### 1. Upload Image Metadata & Get Upload URL
Registers a new image and returns a pre-signed URL to upload the actual binary.
* **Route:** `POST /images`
* **Payload:**
  ```json
  {
    "user_id": "user_123",
    "filename": "vacation.jpg",
    "tags": ["travel", "beach"]
  }
  ```
* **Response (201 Created):**
  ```json
  {
    "message": "Metadata created. Use 'upload_url' to PUT the image binary.",
    "image_id": "0fae0e6a-...",
    "upload_url": "http://localhost:4566/...",
    "metadata": { ... }
  }
  ```

### 2. List Images (With Filters)
Returns a list of image metadata.
* **Route:** `GET /images`
* **Query Parameters (Optional):**
  * `user_id=user_123` (Uses GSI for efficient querying)
  * `tag=travel`
* **Response (200 OK):**
  ```json
  {
    "images":[
      {
        "image_id": "...",
        "user_id": "user_123",
        "s3_key": "user_123/...",
        "tags":["travel"]
      }
    ]
  }
  ```

### 3. View / Download Image
Returns the metadata and a pre-signed GET URL to securely view/download the image binary from S3.
* **Route:** `GET /images/{image_id}`
* **Response (200 OK):**
  ```json
  {
    "image_id": "...",
    "metadata": { ... },
    "download_url": "http://localhost:4566/..."
  }
  ```

### 4. Delete Image
Deletes the image binary from S3 and removes the metadata record from DynamoDB.
* **Route:** `DELETE /images/{image_id}`
* **Response (200 OK):**
  ```json
  {
    "message": "Image deleted successfully"
  }
  ```

---

## Testing

Unit tests are written using `pytest` and `moto` to mock AWS services without requiring LocalStack to be running.

```bash
# Run test suite with coverage
pytest tests/ --cov=src
```

---

## Future Production Improvements
If deploying this to a production AWS environment, the following enhancements would be made:
1. **Authentication:** Implement AWS Cognito Authorizers on the API Gateway to validate JWT tokens and extract the `user_id` securely, rather than trusting the client payload.
2. **CDN / Caching:** Put an Amazon CloudFront distribution in front of the S3 bucket to cache image reads globally and reduce latency.
3. **Event-Driven Processing:** Add an S3 Event Notification to trigger a secondary Lambda function to generate image thumbnails asynchronously whenever a new image is uploaded.
