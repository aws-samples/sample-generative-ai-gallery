import boto3
import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
OBJECT_PATH = os.environ.get('OBJECT_PATH')
PRESIGNED_URL_TTL = int(os.environ.get('PRESIGNED_URL_TTL', 300))

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def generate_unique_id() -> str:
    current_time = datetime.now().strftime("%Y%m%d%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{current_time}-{unique_id}.png"

def generate_presigned_url(object_key: str) -> str:
    return s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': BUCKET_NAME, 'Key': object_key, 'ContentType': 'image/png'},
        ExpiresIn=PRESIGNED_URL_TTL
    )

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        file_uuid = generate_unique_id()
        object_key = f"{OBJECT_PATH}{file_uuid}"
        presigned_url = generate_presigned_url(object_key)

        return create_response(200, {
            'uploadUrl': presigned_url,
            'uuid': file_uuid[:-4]
        })

    except Exception as e:
        return create_response(500, {'error': f'Internal server error: {str(e)}'})