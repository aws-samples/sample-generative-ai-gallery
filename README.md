# GenAI Gallery

![](./docs/images/sample.jpg)

This repository is a sample project that utilizes [Amazon Bedrock](https://aws.amazon.com/bedrock/) for generative AI, to create images of historical figures. It then uses a SageMaker Endpoint to synthesize these images with users' selfie photos, producing composite results. 

This showcase demonstrates the integration of various AWS AI services for creative image generation and manipulation.

## Architecture

Key Components:

- [AWS Amplify](https://aws.amazon.com/amplify/): Provides frontend application hosting (using React).
- [Amazon API Gateway](https://aws.amazon.com/api-gateway/) + [AWS Lambda](https://aws.amazon.com/lambda/): Used as backend API endpoints for image retrieval and upload.
- [Amazon Bedrock](https://aws.amazon.com/bedrock/): A managed service that utilizes foundation models through APIs. It uses the Amazon Titan Image Generator model for image generation and the Claude 3.0 Sonnet model for descriptions.
- [Amazon SageMaker](https://aws.amazon.com/sagemaker/): Deploys the necessary model as an Endpoint to process image synthesis requests.
- [Amazon Rekognition](https://aws.amazon.com/rekognition/): Detects faces in images and videos, and crops the relevant facial areas.

## Deploy

> [!Important]
> - You have installed the latest version of [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
> - You have an [AWS account](https://aws.amazon.com/free/)
> - You have the necessary permissions to create and manage AWS resources
> - You must use a region where [Amazon Bedrock is supported](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html).

### Prerequisites

1. Clone the repository:
    ```
    https://github.com/raphael-shin/my-aws-cdk-sample.git
    ```

### Step 1: Deploy Backend

1. Move backend directory:
    ```
    cd backend
   ```

2. Create a virtual environment:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
   ```

3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Configure your AWS credentials:
    ```
    aws configure
    ```

5. Prepare deploy CDK:
    ```
    cdk bootstrap aws://<account id>/<your-aws-region>
    ```

6. Update the `cdk.context.json` file with your aws region, and other configuration details.
    ```
    {
        "s3_base_bucket_name": "genai-gallery",
        "s3_base_images_path": "images/base/",
        "s3_face_images_path": "images/face/",
        "s3_masked_face_images_path": "images/masked-face/",
        "s3_swapped_face_images_path": "images/swapped-face/",
        "s3_result_images_path": "images/result/",
        "pillow_layer_arn": "arn:aws:lambda:{your-aws-region}:770693421928:layer:Klayers-p38-Pillow:10",
        "numpy_layer_arn": "arn:aws:lambda:{your-aws-region}:770693421928:layer:Klayers-p38-numpy:13"
    }
    ```

6. Deploy CDK stacks:
    ```
    cdk deploy --require-approval never --all
    ```

### Step 2: Run Frontend Application

1. If step 1 is completed successfully, You will receive output similar to the following. The URL of the Amazon API Gateway Endpoint will be output to `ApiGatewayStack.ApiGatewayUrl`, so record that address and use it for frontend deployment.
    ```
    ✅  ApiGatewayStack

    ✨  Deployment time: 68.13s

    Outputs:
    ApiGatewayStack.GenAIGalleryImageApiEndpoint2DF4C2F5 = https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/
    ApiGatewayStack.ApiGatewayUrl = https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/
    Stack ARN:
    arn:aws:cloudformation:us-east-1:xxxxx:stack/ApiGatewayStack/14bb1380-4566-11ef-ac05-0e7a94e90b7d
    ```

3. In the `.env` file of the frontend folder, replace the `{your backend Amazon API Gateway endpoint url}` part of `REACT_APP_API_ENDPOINT={your backend Amazon API Gateway endpoint url}` with the API Gateway Endpoint URL mentioned above.
    ```
    REACT_APP_API_ENDPOINT=https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/
    ```

4. If you were in the backend directory, move to the frontend directory using the command below.
    ```
    cd ../frontend
    ```

5. Install the required dependencies:
    ```
    npm install
    ```

6. Run the application using the command below:
    ```
    npm start
    ```

## Contacts

- [Chulwoo Choi](https://github.com/prorhap)
- [Jinwoo Park](https://github.com/jinuland)
- [Jungseob Shin](https://github.com/raphael-shin)
- [Seongjin Ahn](https://github.com/tjdwlsdlaek)
- [Kihoon Kwon](https://github.com/kyoonkwon)
- [Jisoo Min](https://github.com/Jisoo-Min)
- [Hyeryeong Joo](https://github.com/HyeryeongJoo)

## Contributors

[![genai-gallery contributors](https://contrib.rocks/image?repo=raphael-shin/my-aws-cdk-sample&max=1000)](https://github.com/raphael-shin/my-aws-cdk-sample/graphs/contributors)

## License

This library is licensed under the MIT-0 License. See [the LICENSE file](./LICENSE).
