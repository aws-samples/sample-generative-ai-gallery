# Global Summit 2025 - AI Image Gallery Project

This repository contains three interconnected projects that together form an AI-powered image gallery application:

1. **gallery-backend**: Backend infrastructure and APIs
2. **gallery-frontend**: User interface and frontend application
3. **image-generator**: AI-based image generation utility

## Project Overview

### Gallery Backend

The backend infrastructure is built using AWS CDK and provides the foundation for the entire application. It consists of several key components:

- **API Gateway**: RESTful endpoints for image upload, retrieval, and user agreement management
- **AWS Cognito**: User authentication and authorization
- **DynamoDB**: Data storage for image processing status, display information, and user agreements
- **Lambda Functions**: Serverless processing for image manipulation and business logic
- **S3 Buckets**: Object storage for images and assets
- **SageMaker Endpoints**: AI model deployment for FaceChain and GFPGAN
- **Container Infrastructure**: ECR repositories and CodeBuild pipelines for AI model containers

The backend handles all data processing, storage, and AI model integration, providing a robust foundation for the application.

### Gallery Frontend

The frontend is a React TypeScript application that provides the user interface for the gallery service. Key features include:

- User authentication with AWS Cognito
- Image upload and processing
- Face detection and manipulation
- AI-powered face swapping
- Multi-language support (i18n)
- User agreement management
- QR code generation for sharing

The frontend communicates with the backend APIs to provide a seamless user experience for image processing and management.

### Image Generator

The image generator is a Python-based utility that leverages Amazon Bedrock to create AI-generated images. It includes:

- Integration with Amazon Bedrock's Nova Canvas model for image generation
- Claude 3.5 Sonnet for text processing and prompt engineering
- Configuration for various image styles, historical periods, and attributes
- S3 integration for storing generated images
- DynamoDB integration for tracking image metadata

This component allows the application to generate high-quality base images that can be used in the face swapping process.

## Amazon Bedrock Model Access Setup

Before using the image generator, you need to set up access to the required Amazon Bedrock models:

### 1. Access AWS Bedrock Console

1. Sign in to the AWS Bedrock console: https://console.aws.amazon.com/bedrock/
2. Set the region to `us-east-1` (Nova Canvas model is only available in us-east-1)

### 2. Request Model Access

1. In the left navigation pane, under **Bedrock configurations**, choose **Model access**
2. Choose **Modify model access**
3. Select the following models:
   - Anthropic Claude 3.5 Sonnet
   - Amazon Nova Canvas
4. Choose **Next**
5. For Anthropic models, you must submit use case details
6. Review and accept the terms, then choose **Submit**

### 3. IAM Permissions Setup

To request model access, your IAM role needs the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "aws-marketplace:Subscribe",
                "aws-marketplace:Unsubscribe",
                "aws-marketplace:ViewSubscriptions"
            ],
            "Resource": "*"
        }
    ]
}
```

### 4. S3 Bucket Access Setup

To allow the image generator to save images to S3, you need to configure proper IAM permissions:

1. Go to AWS IAM Console: https://console.aws.amazon.com/iam/
2. Create a new IAM policy with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::amazon-bedrock-gallery-sydney-jungseob",
                "arn:aws:s3:::amazon-bedrock-gallery-sydney-jungseob/*"
            ]
        }
    ]
}
```

3. Attach this policy to the IAM role/user that will be used to run the image generator
4. Make sure the S3 bucket name in the policy matches your actual bucket name

### Important Notes

- Nova Canvas model is only available in `us-east-1` region
- Model access approval may take several minutes
- If model access is denied, contact AWS support or choose alternative models

## Deployment Instructions

Follow these steps to deploy the complete application:

### 1. Deploy Gallery Backend

First, deploy the backend infrastructure:

```bash
cd gallery-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate unique ID and update cdk.context.json
UNIQUE_ID=$(openssl rand -hex 4)
sed -i '' "s/<your-unique-id>/$UNIQUE_ID/g" cdk.context.json

cdk synth
cdk deploy --all
```

This will create all necessary AWS resources including API Gateway, Lambda functions, DynamoDB tables, S3 buckets, and SageMaker endpoints.

### 2. Generate Base Images

After the backend is deployed, use the image generator to create base images:

```bash
cd ../image-generator
pip install -r requirements.txt
python generate_image.py
```

This will generate images using Amazon Bedrock and store them in the configured S3 bucket, making them available for the face swapping process.

### 3. Deploy Gallery Frontend

Finally, deploy the frontend application:

```bash
cd ../gallery-frontend
npm install
# Update .env file with your backend API endpoints
npm run build:prod
# Deploy the build directory to your hosting service of choice
```

## Testing the Application

Once all components are deployed, you can test the complete workflow:

1. Access the frontend application
2. Create an account and sign in
3. Upload a photo for face swapping
4. Select a base image generated by the image generator
5. Process the image using the AI models deployed in the backend
6. View and share your generated images

## Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│ Gallery Frontend│────▶│  Gallery Backend│◀────│ Image Generator │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                       AWS Infrastructure                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Requirements

- AWS Account with appropriate permissions
- Node.js v14 or higher
- Python 3.8 or higher
- AWS CDK installed and configured
- AWS CLI installed and configured

## Contributing

Please refer to the individual project READMEs for specific contribution guidelines.
