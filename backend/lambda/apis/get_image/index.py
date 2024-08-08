import base64
import boto3
import json
import os
from typing import Dict, Any, Tuple
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
OBJECT_PATH = os.environ.get('OBJECT_PATH')
PRESIGNED_URL_TTL = int(os.environ.get('PRESIGNED_URL_TTL', 1800))

MODELS = [
    'anthropic.claude-3-5-sonnet-20240620-v1:0',
    'anthropic.claude-3-sonnet-20240229-v1:0',
    'anthropic.claude-3-haiku-20240307-v1:0'
]

def call_bedrock_model(model_id, body):
    try:
        response = bedrock.invoke_model(
            body=body,
            modelId=model_id,
            contentType='application/json',
            accept='application/json'
        )
        response_body = json.loads(response['body'].read())
        return json.loads(response_body['content'][0]['text']), model_id
    except ClientError as e:
        if e.response['Error']['Code'] == 'ThrottlingException':
            print(f"Model {model_id} quota exceeded. Trying next model.")
            return None
        else:
            raise e

def invoke_bedrock_api(prompt, image_data) -> Tuple[Dict, str]:
    base64_image = base64.b64encode(image_data).decode('utf-8')

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    })

    for model in MODELS:
        result = call_bedrock_model(model, body)
        if result is not None:
            return result

    raise Exception("All models failed due to quota limits")

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        uuid = event['pathParameters']['uuid']
        if not uuid:
            return create_response(400, {'error': 'Invalid request: Missing UUID'})

        object_key = f"{OBJECT_PATH}{uuid}.png"
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_key)
        image_data = response['Body'].read()

        prompt = "Create a fictional past life story based on the person in the image. Limit the story to 150 characters. Output the result in JSON format in English, Korean, and Japanese. example: {'ko': '한글', 'en': 'English', 'ja': '日本語'}"
        result, used_model = invoke_bedrock_api(prompt, image_data)
        
        presigned_url = generate_presigned_url(object_key)

        return create_response(200, {
            'downloadUrl': presigned_url,
            'uuid': uuid,
            'story': result,
            'model': used_model
        })


    except KeyError:
        return create_response(400, {'error': 'Invalid request: Missing path parameters'})
    except Exception as e:
        return create_response(500, {'error': f'Internal server error: {str(e)}'})

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def generate_presigned_url(object_key: str) -> str:
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': object_key},
        ExpiresIn=PRESIGNED_URL_TTL
    )