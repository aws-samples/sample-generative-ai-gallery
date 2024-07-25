import boto3
import json
import os
from typing import Dict, Any

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
OBJECT_PATH = os.environ.get('OBJECT_PATH')
PRESIGNED_URL_TTL = int(os.environ.get('PRESIGNED_URL_TTL', 1800))

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        uuid = event['pathParameters']['uuid']
        if not uuid:
            return create_response(400, {'error': 'Invalid request: Missing UUID'})

        object_key = f"{OBJECT_PATH}{uuid}.png"
        presigned_url = generate_presigned_url(object_key)

        return create_response(200, {
            'downloadUrl': presigned_url,
            'uuid': uuid
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