# Image Generator

A Python-based utility that leverages Amazon Bedrock to create AI-generated images.

## Overview

This project uses Amazon Bedrock's Nova Canvas model to generate high-quality AI images. The generated images are used as base images in the face swapping process.

## Key Features

- **Amazon Bedrock Nova Canvas Model Integration**: High-quality image generation
- **Claude 3.5 Sonnet**: Text processing and prompt engineering
- **Various Image Styles**: Historical periods, attributes, and diverse settings
- **S3 Integration**: Store generated images
- **DynamoDB Integration**: Track image metadata

## Prerequisites

### 1. Amazon Bedrock Model Access Setup

#### Access AWS Bedrock Console

1. Sign in to the AWS Bedrock console: https://console.aws.amazon.com/bedrock/
2. Set the region to `us-east-1` (Nova Canvas model is only available in us-east-1)

#### Request Model Access

1. In the left navigation pane, under **Bedrock configurations**, choose **Model access**
2. Choose **Modify model access**
3. Select the following models:
   - Anthropic Claude 3.5 Sonnet
   - Amazon Nova Canvas
4. Choose **Next**
5. For Anthropic models, you must submit use case details
6. Review and accept the terms, then choose **Submit**

### 2. IAM Permissions Setup

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

### 3. S3 Bucket Access Setup

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
                "arn:aws:s3:::your-s3-bucket-name",
                "arn:aws:s3:::your-s3-bucket-name/*"
            ]
        }
    ]
}
```

3. Attach this policy to the IAM role/user that will be used to run the image generator
4. Make sure the S3 bucket name in the policy matches your actual bucket name

### 4. System Requirements

- Python 3.8 or higher
- AWS CLI installed and configured
- Required Python packages (see requirements.txt)

## Installation and Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd image-generator
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables Setup

Create a `.env` file and add the following content:

```env
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
DYNAMODB_TABLE_NAME=your-dynamodb-table-name
```

## Usage

### Basic Image Generation

```bash
python generate_image.py
```

### Configuration File Modification

You can adjust the following settings in the `config.py` file:

- Image styles
- Historical periods
- Attributes and characteristics
- Number of images to generate

### Advanced Usage

Generate images with specific prompts:

```python
from image_generator import ImageGenerator

generator = ImageGenerator()
image_url = generator.generate_image(
    prompt="A portrait of a historical figure in Renaissance style",
    style="realistic",
    period="renaissance"
)
```

## Configuration Options

### Image Styles

- `realistic`: Realistic style
- `artistic`: Artistic style
- `cartoon`: Cartoon style
- `abstract`: Abstract style

### Historical Periods

- `ancient`: Ancient
- `medieval`: Medieval
- `renaissance`: Renaissance
- `modern`: Modern

### Attributes

- `age`: Age
- `gender`: Gender
- `ethnicity`: Ethnicity
- `profession`: Profession

## Output

Generated images are stored in the following locations:

- **S3**: `s3://your-bucket-name/images/generated/`
- **Metadata**: Stored in DynamoDB table
- **Local**: `output/` directory (optional)

## Monitoring and Logging

- Log monitoring through CloudWatch Logs
- Generation status tracking through DynamoDB
- S3 event notifications can be configured

## Troubleshooting

### Common Issues

1. **Model Access Denied**
   - Check model access status in AWS Bedrock console
   - Verify IAM permissions

2. **S3 Upload Failed**
   - Check S3 bucket permissions
   - Verify AWS credentials

3. **Out of Memory**
   - Reduce batch size
   - Use larger instances

### Log Checking

```bash
# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/image-generator"

# Check local logs
tail -f logs/image-generator.log
```

## Performance Optimization

- Batch processing for generating multiple images simultaneously
- Prevent duplicate requests through caching
- Improve throughput with asynchronous processing

## Security Considerations

- Apply AWS IAM least privilege principle
- Use AWS Secrets Manager for sensitive information
- Configure network access controls

## Cost Optimization

- Clean up unused resources
- Consider using reserved instances
- Monitor CloudWatch costs

## Monthly Cost Estimation

### AWS Service Costs

#### Amazon Bedrock
- **Nova Canvas**: $0.08 per image (1024x1024 resolution)
- **Claude 3.5 Sonnet**: $0.003 per 1K input tokens, $0.015 per 1K output tokens
- **Estimated monthly cost for 100 images**: $8-12

#### Amazon SageMaker (GPU Instances)
- **Combined FaceChain + GFPGAN Endpoint**: ml.g4dn.xlarge - $0.736 per hour
- **Monthly GPU cost (24/7)**: $529.92

#### Amazon S3
- **Storage**: $0.023 per GB per month
- **Data transfer**: $0.09 per GB (outbound)
- **Estimated monthly cost for 1GB storage**: $0.02-0.10

#### Amazon DynamoDB
- **Read/Write capacity**: $0.25 per RCU, $1.25 per WCU
- **Storage**: $0.25 per GB per month
- **Estimated monthly cost for light usage**: $5-15

#### AWS Lambda
- **Compute time**: $0.20 per 1M requests, $0.0000166667 per GB-second
- **Estimated monthly cost for 1000 invocations**: $1-5

#### CloudWatch Logs
- **Ingestion**: $0.50 per GB
- **Storage**: $0.03 per GB per month
- **Estimated monthly cost**: $2-8

#### Amazon API Gateway
- **REST API**: $3.50 per million API calls
- **Data transfer**: $0.09 per GB
- **Estimated monthly cost for 10K requests**: $0.04-0.10

#### AWS Cognito
- **MAU (Monthly Active Users)**: $0.0055 per MAU
- **Estimated monthly cost for 100 users**: $0.55

### Usage Scenarios

#### Light Usage (50 images/month, 8 hours/day GPU usage)
- **Total estimated cost**: $550-650/month
- **Breakdown**:
  - Bedrock: $4-6
  - SageMaker GPU: $176-235 (8 hours/day)
  - S3: $0.01-0.05
  - DynamoDB: $3-8
  - Lambda: $0.5-2
  - CloudWatch: $1-3
  - API Gateway: $0.04-0.10
  - Cognito: $0.55

#### Medium Usage (200 images/month, 16 hours/day GPU usage)
- **Total estimated cost**: $650-850/month
- **Breakdown**:
  - Bedrock: $16-24
  - SageMaker GPU: $353-471 (16 hours/day)
  - S3: $0.05-0.20
  - DynamoDB: $8-20
  - Lambda: $2-8
  - CloudWatch: $3-10
  - API Gateway: $0.04-0.10
  - Cognito: $0.55

#### Heavy Usage (500 images/month, 24/7 GPU usage)
- **Total estimated cost**: $750-950/month
- **Breakdown**:
  - Bedrock: $40-60
  - SageMaker GPU: $529.92 (24/7)
  - S3: $0.10-0.50
  - DynamoDB: $15-35
  - Lambda: $5-15
  - CloudWatch: $5-15
  - API Gateway: $0.04-0.10
  - Cognito: $0.55

### Cost Optimization Tips

1. **GPU Instance Management**: 
   - Use auto-scaling to scale down during low usage periods
   - Consider using Spot instances for non-critical workloads
   - Implement automatic shutdown during off-hours

2. **Batch Processing**: Generate multiple images in a single session to reduce API calls
3. **Image Resolution**: Use appropriate resolution for your needs (lower resolution = lower cost)
4. **Storage Management**: Regularly clean up unused images from S3
5. **DynamoDB Optimization**: Use on-demand capacity for variable workloads
6. **Lambda Optimization**: Optimize function execution time and memory allocation

### GPU Instance Cost Breakdown

#### ml.g4dn.xlarge Specifications
- **vCPUs**: 4
- **Memory**: 16 GB
- **GPU**: 1x NVIDIA T4
- **Storage**: 125 GB NVMe SSD
- **Hourly Cost**: $0.736
- **Daily Cost (24 hours)**: $17.664
- **Monthly Cost (30 days)**: $529.92
- **Note**: Single instance hosts both FaceChain and GFPGAN models

#### Cost Optimization for GPU Instances
- **Auto-scaling**: Scale to 0 instances during off-hours
- **Spot Instances**: Up to 90% cost savings (if available)
- **Reserved Instances**: 1-year or 3-year commitment for 30-60% savings
- **Scheduled Scaling**: Automatically start/stop based on usage patterns

### Free Tier Considerations

- **AWS Lambda**: 1M free requests per month
- **Amazon S3**: 5GB storage for 12 months
- **Amazon DynamoDB**: 25GB storage and 25 WCU/25 RCU for 12 months
- **CloudWatch Logs**: 5GB data ingestion and 5GB data archive for 12 months
- **Amazon API Gateway**: 1M API calls per month for 12 months
- **AWS Cognito**: 50,000 MAUs for 12 months

> **Note**: 
> - Prices are based on US East (N. Virginia) region as of 2024
> - GPU costs are the largest component due to SageMaker endpoints running 24/7
> - Consider implementing auto-scaling to reduce GPU costs during low usage periods
> - Actual costs may vary based on usage patterns, region, and AWS pricing changes
> - Always check the latest AWS pricing for accurate estimates

## License

This project is released under the MIT License.

## Contributing

Bug reports, feature requests, and pull requests are welcome.

## Contact

For project-related inquiries, please create an issue.
