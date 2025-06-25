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

## License

This project is released under the MIT License.

## Contributing

Bug reports, feature requests, and pull requests are welcome.

## Contact

For project-related inquiries, please create an issue.
