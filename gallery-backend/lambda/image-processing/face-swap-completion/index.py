import json
import boto3
import os
import urllib.request
import urllib.error
import io
from datetime import datetime

DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME = os.environ['DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME']
DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME = os.environ['DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME']

ddb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    s3_event = event['Records'][0]['s3']
    encoded_object_key = s3_event['object']['key']
    result_object_key = urllib.parse.unquote_plus(encoded_object_key) # user's result image
    result_object_filename = os.path.basename(result_object_key) # result_object_filename: {current_time}-{user_id}-{theme}-{gender}-{skin}-{unique_id}.jpeg
    uuid = os.path.splitext(result_object_filename)[0]
    userId = uuid.split('-')[1]
    theme = uuid.split('-')[2]
    gender = uuid.split('-')[3]
    skin = uuid.split('-')[4]

    # get process image info
    ddb_response = ddb_client.query(
        TableName=DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME,
        KeyConditionExpression='#pk = :pk',
        ExpressionAttributeNames={
            '#pk': 'PK'
        },
        ExpressionAttributeValues={
            ':pk': {'S': f'#UUID#{uuid}'}
        }
    )
    
    if not ddb_response['Items']:
        raise Exception(f"Could not find image with uuid({uuid})")

    process_image_info = ddb_response['Items'][0]
    base_image_object_key = process_image_info['base_image_object_key']['S']
    base_story = process_image_info['base_story']['S']
    theme = process_image_info['theme']['S']
    gender = process_image_info['gender']['S']
    skin = process_image_info['skin']['S']
    
    try:
        response = ddb_client.query(
            TableName=DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME,
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': {'S': f'#USERID#{userId}'}
            }
        )
        
        current_time = datetime.now().isoformat()
        
        if response['Items']:
            # if there is an item, update it (#USERID#{user_id})
            ddb_client.update_item(
                TableName=DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME,
                Key={
                    'PK': {'S': f'#USERID#{userId}'}
                },
                UpdateExpression='SET #uuid_attr = :uuid, base_image_object_key = :base_image_object_key, result_object_key = :result_object_key, base_story = :base_story, theme = :theme, updated_at = :updated_at, gender = :gender, skin = :skin',
                ExpressionAttributeNames={
                    '#uuid_attr': 'uuid',
                },
                ExpressionAttributeValues={
                    ':uuid': {'S': uuid},
                    ':base_image_object_key': {'S': base_image_object_key},
                    ':result_object_key': {'S': result_object_key},
                    ':base_story': {'S': base_story},
                    ':theme': {'S': theme},
                    ':gender': {'S': gender},
                    ':skin': {'S': skin},
                    ':updated_at': {'S': current_time}
                }
            )
        else:
            ddb_client.put_item(
                TableName=DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME,
                Item={
                    'PK': {'S': f'#USERID#{userId}'},
                    'uuid': {'S': uuid},
                    'userId': {'S': userId},
                    'gender': {'S': gender},
                    'skin': {'S': skin},
                    'base_image_object_key': {'S': base_image_object_key},
                    'result_object_key': {'S': result_object_key},
                    'base_story': {'S': base_story},
                    'theme': {'S': theme},
                    'updated_at': {'S': current_time},
                    'created_at': {'S': current_time}
                }
            )
    except Exception as e:
        print(f"error: {str(e)}")
        raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps('Face swap complete')
    }
