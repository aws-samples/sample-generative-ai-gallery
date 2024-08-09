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
    print(f"Invoking Bedrock model: {model_id}")
    try:
        response = bedrock.invoke_model(
            body=body,
            modelId=model_id,
            contentType='application/json',
            accept='application/json'
        )
        print(f"Bedrock API response: {response}")
        response_body = json.loads(response['body'].read())
        print(f"Bedrock API response: {response_body}")
        print(f"Bedrock API response: {response_body['content'][0]['text']}")
        return response_body['content'][0]['text'], model_id
    except ClientError as e:
        if e.response['Error']['Code'] == 'ThrottlingException':
            print(f"Model {model_id} quota exceeded. Trying next model.")
            return None
        else:
            print(f"Error invoking Bedrock model: {e}")
            raise e
    except Exception as e:
        print(f"Error invoking Bedrock model: {e}")
        raise e

def invoke_bedrock_api(prompt, image_data) -> Tuple[Dict, str]:
    base64_image = base64.b64encode(image_data).decode('utf-8')
    body = json.dumps({
        "anthropic_version": "",
        "max_tokens": 2000,
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
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "<JSON>"}]
            }
        ]
    })

    for model in MODELS:
        result = call_bedrock_model(model, body)
        if result is not None:
            return result

    raise Exception("All models failed due to quota limits")

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        uuid = event['pathParameters']['uuid']
        if not uuid:
            return create_response(400, {'error': 'Invalid request: Missing UUID'})

        object_key = f"{OBJECT_PATH}{uuid}.png"
        print(f"Fetching image from S3: {object_key}")
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_key)
        image_data = response['Body'].read()

        prompt = """
        당신은 이미지 속 인물과 사물을 분석하고, 가상의 전생 스토리를 만들어주세요.
        1.특정 개인을 식별하는 것은 금지됩니다. 스토리의 주인공은 실존하지 않는 가상의 인물이어야 합니다.
        2.스토리의 인물은 당신이라는 명칭으로 시작해야 합니다.
        3.일대기 스토리의 글자는 150개로 제한해주세요.
        4. 당신이 분석한 내용을 제외하고, 일대기 스토리만 영어, 한글, 일본어로 json 형태로 출력해주세요. json 형태 외 다른 내용은 아웃풋으로 포함하지 않습니다.
        예:: {'ko': '한글', 'en': 'English', 'ja': '日本語'}
        """
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