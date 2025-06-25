#!/bin/bash

# Bedrock Gallery Admin Deployment Script

set -e

echo "🚀 Starting deployment of Bedrock Gallery Admin..."

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless Framework not found. Installing..."
    npm install -g serverless
fi

# Check if required plugins are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Serverless plugins..."
    npm init -y
    npm install serverless-python-requirements
fi

# Deploy the API
echo "🔧 Deploying API to AWS Lambda..."
serverless deploy --stage prod

# Get the outputs
echo "📋 Getting deployment outputs..."
API_URL=$(serverless info --stage prod --verbose | grep -o 'https://[^/]*\.execute-api\.[^/]*\.amazonaws\.com/prod' | head -1)
CLOUDFRONT_URL=$(serverless info --stage prod --verbose | grep -A 10 "Stack Outputs" | grep "CloudFrontURL:" | cut -d' ' -f2)
FRONTEND_BUCKET=$(serverless info --stage prod --verbose | grep -A 10 "Stack Outputs" | grep "FrontendBucket:" | cut -d' ' -f2)

echo "✅ API deployed successfully!"
echo "📍 API URL: $API_URL"
echo "📍 CloudFront URL: $CLOUDFRONT_URL"
echo "📍 Frontend Bucket: $FRONTEND_BUCKET"

# Update frontend config with production API URL
echo "🔧 Updating frontend configuration..."
sed -i.bak "s|BASE_URL: 'http://localhost:5001'|BASE_URL: '$API_URL'|g" frontend/js/config.js

# Upload frontend to S3
echo "📤 Uploading frontend to S3..."
aws s3 sync frontend/ s3://$FRONTEND_BUCKET/ --delete

# Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Origins.Items[0].DomainName=='$FRONTEND_BUCKET.s3.amazonaws.com'].Id" --output text)
if [ ! -z "$DISTRIBUTION_ID" ]; then
    aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
fi

# Restore original config file
mv frontend/js/config.js.bak frontend/js/config.js

echo "🎉 Deployment completed successfully!"
echo ""
echo "🌐 Your admin panel is available at: $CLOUDFRONT_URL"
echo "🔗 API endpoint: $API_URL"
echo ""
echo "⚠️  Note: It may take a few minutes for CloudFront to propagate changes."
