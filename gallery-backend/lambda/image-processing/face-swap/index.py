import json
import boto3
import os
import urllib.parse

ddb_client = boto3.client('dynamodb')
sagemaker_runtime = boto3.client('sagemaker-runtime')

BUCKET_NAME = os.environ['BUCKET_NAME']
RESULT_OBJECT_PATH = os.environ['RESULT_OBJECT_PATH']
FACECHAIN_SAGEMAKER_ENDPOINT_NAME = os.environ['FACECHAIN_SAGEMAKER_ENDPOINT_NAME']
GFPGAN_SAGEMAKER_ENDPOINT_NAME = os.environ['GFPGAN_SAGEMAKER_ENDPOINT_NAME']
DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME = os.environ['DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME']

def lambda_handler(event, context):
    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    encoded_object_key = s3_event['object']['key']
    source_object_key = urllib.parse.unquote_plus(encoded_object_key) # user's cropped face image
    source_object_filename = os.path.basename(source_object_key) # source_object_filename: {current_time}-{user_id}-{theme}-{gender}-{skin}-{unique_id}.jpeg
    uuid = os.path.splitext(source_object_filename)[0] 
    user_id = uuid.split('-')[1]
    theme = uuid.split('-')[2]
    gender = uuid.split('-')[3]
    skin = uuid.split('-')[4]
    
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
    
    target_object_key = ddb_response['Items'][0]['base_image_object_key']['S']
    output_object_key = os.path.join(RESULT_OBJECT_PATH, source_object_filename)

    request_body = {
        'uuid': uuid,
        'bucket': BUCKET_NAME,
        'source': source_object_key,
        'target': target_object_key,
        'output': output_object_key
    }
    
    sagemaker_runtime.invoke_endpoint(
        EndpointName=FACECHAIN_SAGEMAKER_ENDPOINT_NAME,
        ContentType='application/json',
        Body=json.dumps(request_body)
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Face swap complete')
    }