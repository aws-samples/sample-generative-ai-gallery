import boto3
import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any

s3_client = boto3.client('s3')
ddb_client = boto3.client('dynamodb')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME = os.environ.get('DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME')

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST'
        }
    }

def generate_presigned_url(object_key: str) -> str:
    return s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': object_key,
            'ResponseContentType': 'image/jpeg'
        },
        ExpiresIn='300'
    )

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    if event['httpMethod'] == 'OPTIONS':
        return create_response(200, {})
    
    if event['httpMethod'] != 'GET':
        return create_response(405, {'error': f"{event['httpMethod']} Methods are not allowed."})
    
    try:
        # path parameter에서 userId 가져오기
        path_parameters = event.get('pathParameters', {})
        user_id = path_parameters.get('userId')

        if not user_id:
            return create_response(400, {'error': 'Bad Request: userId is required.'})
        
        # DynamoDB에서 user_id에 해당하는 아이템 조회
        response = ddb_client.get_item(
            TableName=DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME,
            Key={
                'PK': {'S': f'#USERID#{user_id}'}
            }
        )
        
        # 조회된 아이템이 있는지 확인
        item = response.get('Item')
        if not item:
            return create_response(404, {'error': 'User not found'})

        uuid = item.get('uuid', {}).get('S')
        base_image_object_key = item.get('base_image_object_key', {}).get('S')
        result_object_key = item.get('result_object_key', {}).get('S')
        theme = item.get('theme', {}).get('S')
        gender = item.get('gender', {}).get('S')
        skin = item.get('skin', {}).get('S')
        base_story = item.get('base_story', {}).get('S')
        presigned_url = generate_presigned_url(result_object_key)

        return create_response(200, {
            'imageUrl': presigned_url,
            'story': base_story,
            'theme': theme,
            'gender': gender,
            'skin': skin,
            'uuid': uuid,
            'userId': user_id
        })

    except Exception as e:
        return create_response(500, {'error': f'Internal server error: {str(e)}'})