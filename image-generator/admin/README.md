# Bedrock Gallery Admin Panel

A serverless admin panel for managing Bedrock-generated images with secure S3 + CloudFront deployment.

## Architecture

- **Backend**: AWS Lambda + API Gateway (Pure Python API)
- **Frontend**: Static HTML/CSS/JS hosted on S3 + CloudFront
- **Security**: Private S3 bucket with CloudFront Origin Access Control (OAC)

## Features

- ✅ Image gallery with pagination
- ✅ Advanced filtering (period, gender, skin tone, profession, style)
- ✅ Bulk image deletion
- ✅ Individual image management
- ✅ Responsive design
- ✅ Secure deployment (no public S3 access)
- ✅ Pure Python Lambda (no external dependencies)

## Local Development

### 1. Use Existing Flask App for Local Testing

For local development and testing, simply use the existing Flask application in the parent directory:

```bash
# Navigate to the main image-generator directory
cd ../
python app.py
```

The Flask app will start at `http://localhost:5000` with all the same functionality as the production admin panel.

### 2. Update Frontend Configuration for Local Testing

Update `frontend/js/config.js` to point to the local Flask server:

```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000',  // Local Flask server
    // BASE_URL: 'https://5yi9e07ex6.execute-api.us-east-1.amazonaws.com/prod',  // Production
    // ...
};
```

### 3. Serve Frontend Locally

```bash
cd frontend
python -m http.server 8000
```

Access the admin panel at `http://localhost:8000`

**Perfect for Development**: The existing Flask app (`../app.py`) provides identical functionality to the production admin panel, making local development seamless without any Lambda setup!

## Production Deployment

### Prerequisites

1. AWS CLI configured with appropriate permissions
2. Existing S3 bucket and DynamoDB table (from main app)

### Deploy

```bash
./deploy.sh
```

This script will:
1. Deploy the API to AWS Lambda
2. Create a private S3 bucket for frontend
3. Set up CloudFront distribution with OAC
4. Upload frontend files to S3
5. Configure proper security settings

### Manual Deployment Steps

If you prefer manual deployment:

#### 1. Deploy API

```bash
aws cloudformation deploy --template-file template.yaml --stack-name bedrock-gallery-admin --capabilities CAPABILITY_IAM --parameter-overrides Stage=prod AdminBucketName=your-bucket-name --region us-east-1
```

#### 2. Update Frontend Config

Update `frontend/js/config.js` with your API Gateway URL:

```javascript
const API_CONFIG = {
    BASE_URL: 'https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod',
    // ...
};
```

#### 3. Upload Frontend

```bash
aws s3 sync frontend/ s3://your-frontend-bucket/frontend/ --delete
```

## Security Features

### S3 Security
- ✅ Block all public access
- ✅ Server-side encryption (AES256)
- ✅ CloudFront Origin Access Control (OAC)
- ✅ Bucket policy restricts access to CloudFront only

### API Security
- ✅ CORS properly configured
- ✅ IAM roles with minimal permissions
- ✅ HTTPS only via CloudFront

### CloudFront Security
- ✅ HTTPS redirect enforced
- ✅ Proper caching policies
- ✅ Custom error pages for SPA routing

## Configuration

### AWS Resources Required

- S3 bucket: `amazon-bedrock-gallery-global-f0154ca1` (images)
- DynamoDB table: `ddb-amazon-bedrock-gallery-base-resource` (metadata)

### IAM Permissions

The Lambda function needs:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::amazon-bedrock-gallery-global-f0154ca1",
                "arn:aws:s3:::amazon-bedrock-gallery-global-f0154ca1/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:Query",
                "dynamodb:DeleteItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:*:table/ddb-amazon-bedrock-gallery-base-resource"
            ]
        }
    ]
}
```

## API Endpoints

- `GET /api/images` - List images with filtering and pagination
- `GET /api/images/{key}` - Get image details
- `DELETE /api/images/{key}` - Delete single image
- `POST /api/images/delete-multiple` - Delete multiple images

## Cost Optimization

- CloudFront PriceClass_100 (US, Canada, Europe only)
- Caching optimized for static assets
- API caching disabled for dynamic content
- Lambda timeout set to 30 seconds
- Pure Python Lambda (minimal package size: 3KB)
