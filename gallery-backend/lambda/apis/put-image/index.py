import boto3
import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any
import random

s3_client = boto3.client('s3')
ddb_client = boto3.client('dynamodb')
BUCKET_NAME = os.environ['BUCKET_NAME']
OBJECT_PATH = os.environ['OBJECT_PATH']
DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME = os.environ['DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME']
DDB_AMAZON_BEDROCK_GALLERY_BASE_RESOURCE_TABLE_NAME = os.environ['DDB_AMAZON_BEDROCK_GALLERY_BASE_RESOURCE_TABLE_NAME']

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

def generate_image_ojbect_name(uuid: str, user_id: str, theme: str, gender: str, skin: str) -> str:
    current_time = datetime.now().strftime("%Y%m%d%S")
    return f"{current_time}-{user_id}-{theme}-{gender}-{skin}-{uuid}"

def generate_presigned_url(object_key: str) -> str:
    return s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': BUCKET_NAME, 
            'Key': object_key, 
            'ContentType': 'image/jpeg'
        },
        ExpiresIn='300'
    )

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    if event['httpMethod'] == 'OPTIONS':
        return create_response(200, {})
    
    if event['httpMethod'] != 'POST':
        return create_response(405, {'error': f"{event['httpMethod']} Methods are not allowed."})
    
    try:
        # request body parse (if body is string, decode json)
        body = event.get('body')
        if body is None:
            return create_response(400, {'error': 'Bad Request: Body is required.'})
        
        # if body is json string, parse
        if isinstance(body, str):
            body = json.loads(body)
        
        user_id = body.get('userId')
        theme = body.get('theme')
        gender = body.get('gender')
        skin = body.get('skin')
        
        # required parameter check
        if not user_id or not theme or not gender or not skin:
            return create_response(400, {'error': 'Bad Request: userId, theme, gender and skin values are required.'})
        
        # get random base resource
        ddb_response = ddb_client.query(
            TableName=DDB_AMAZON_BEDROCK_GALLERY_BASE_RESOURCE_TABLE_NAME,
            KeyConditionExpression="#pk = :pk",
            ExpressionAttributeNames={
                '#pk': 'PK'
            },
            ExpressionAttributeValues={
                ':pk': {'S': f'#THEME#{theme}#GENDER#{gender}#SKIN#{skin}'},
            }
        )
    
        if not ddb_response['Items']:
            raise Exception(f"Could not find image with theme({theme}) and gender({gender}) and skin({skin})")
        
        random_item = random.choice(ddb_response['Items'])
        
        # unique image name create
        unique_id = str(uuid.uuid4())[:8]
        # uuid and userId and theme info to ddb with proper DynamoDB types
        image_object_name = generate_image_ojbect_name(unique_id, user_id, theme, gender, skin)
        ddb_client.put_item(
            TableName=DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME,
            Item={
                'PK': {'S': f'#UUID#{image_object_name}'},
                'userId': {'S': user_id},
                'theme': {'S': theme},
                'gender': {'S': gender},
                'skin': {'S': skin},
                'base_image_object_key': {'S': random_item['base_image_object_key']['S']},
                'base_story': {'S': random_item['story']['S']},
                'updated_at': {"S": datetime.now().isoformat()},
                'created_at': {"S": datetime.now().isoformat()}
            }
        )

        # userId and theme info to path (OBJECT_PATH is the default path on S3)
        image_object_key = os.path.join(OBJECT_PATH, f'{image_object_name}.jpeg')
        image_upload_presigned_url = generate_presigned_url(image_object_key)

        return create_response(200, {
            'uuid': unique_id,
            'uploadUrl': image_upload_presigned_url
        })

    except Exception as e:
        return create_response(500, {'error': f'Internal server error: {str(e)}'})