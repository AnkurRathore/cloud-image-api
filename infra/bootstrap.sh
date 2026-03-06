#!/usr/bin/env bash
# ---------------------------------------------------------------
# bootstrap.sh
# Creates all AWS resources required by image-service in LocalStack.
# 
# ---------------------------------------------------------------

set -euo pipefail

# ── Config ──────────────────────────────────────────────────────
ENDPOINT="http://localhost:4566"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
BUCKET="${S3_BUCKET_NAME:-image-service-bucket}"
TABLE="${DYNAMO_TABLE:-images}"

export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
export AWS_DEFAULT_REGION="${REGION}"

AWS_LOCAL="aws --endpoint-url=${ENDPOINT} --region=${REGION}"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Wait for LocalStack ─────────────────────────────────────────
log_info "Waiting for LocalStack to be ready..."
for i in $(seq 1 30); do
  if curl -sf "${ENDPOINT}/_localstack/health" | grep -q '"s3": "available"'; then
    log_ok "LocalStack is ready."
    break
  fi
  if [ "$i" -eq 30 ]; then
    log_error "LocalStack did not become ready in time. Is it running? Try: make up"
  fi
  sleep 2
done

# ── S3 Bucket ───────────────────────────────────────────────────
log_info "Creating S3 bucket: ${BUCKET}"
if $AWS_LOCAL s3api head-bucket --bucket "${BUCKET}" 2>/dev/null; then
  log_ok "S3 bucket '${BUCKET}' already exists — skipping."
else
  $AWS_LOCAL s3api create-bucket --bucket "${BUCKET}" \
    --create-bucket-configuration LocationConstraint="${REGION}" 2>/dev/null || \
  $AWS_LOCAL s3api create-bucket --bucket "${BUCKET}"  # us-east-1 doesn't use LocationConstraint

  # Block all public access
  $AWS_LOCAL s3api put-public-access-block \
    --bucket "${BUCKET}" \
    --public-access-block-configuration \
      "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

  log_ok "S3 bucket '${BUCKET}' created."
fi

# ── DynamoDB Table ──────────────────────────────────────────────
log_info "Creating DynamoDB table: ${TABLE}"
if $AWS_LOCAL dynamodb describe-table --table-name "${TABLE}" 2>/dev/null; then
  log_ok "DynamoDB table '${TABLE}' already exists — skipping."
else
  $AWS_LOCAL dynamodb create-table \
    --table-name "${TABLE}" \
    --attribute-definitions \
      AttributeName=image_id,AttributeType=S \
      AttributeName=user_id,AttributeType=S \
      AttributeName=upload_date,AttributeType=S \
    --key-schema \
      AttributeName=image_id,KeyType=HASH \
    --global-secondary-indexes \
      "[
        {
          \"IndexName\": \"UserIdIndex\",
          \"KeySchema\": [
            {\"AttributeName\": \"user_id\", \"KeyType\": \"HASH\"},
            {\"AttributeName\": \"upload_date\", \"KeyType\": \"RANGE\"}
          ],
          \"Projection\": {\"ProjectionType\": \"ALL\"},
          \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        },
        {
          \"IndexName\": \"UploadDateIndex\",
          \"KeySchema\": [
            {\"AttributeName\": \"upload_date\", \"KeyType\": \"HASH\"}
          ],
          \"Projection\": {\"ProjectionType\": \"ALL\"},
          \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        }
      ]" \
    --billing-mode PAY_PER_REQUEST \
    --output table

  log_ok "DynamoDB table '${TABLE}' created with GSIs: UserIdIndex, UploadDateIndex."
fi

# ── Summary ─────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_ok "Bootstrap complete!"
echo "  S3 Bucket   : ${BUCKET}"
echo "  DynamoDB    : ${TABLE}"
echo "  Region      : ${REGION}"
echo "  Endpoint    : ${ENDPOINT}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  make test       — run unit tests"
echo "  make invoke-upload  — test upload via curl"
echo ""