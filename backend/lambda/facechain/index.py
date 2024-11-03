import json
import boto3
import os
import urllib.parse
import time
import random
from typing import Dict, Any

# Initialize AWS clients
sagemaker_runtime = boto3.client('sagemaker-runtime')
s3_client = boto3.client('s3')

# Constants
MAX_WAIT_TIME = 30  # Maximum wait time in seconds
CHECK_INTERVAL = 1  # Time between checks in seconds
BASE_IMAGE_PREFIX = 'images/base/'

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        s3_event = event['Records'][0]['s3']
        input_data = prepare_input_data(s3_event)
        invoke_sagemaker_endpoint(input_data)
        
        output_url = wait_for_output_file(input_data['bucket'], input_data['output'])
        
        return create_success_response(output_url)
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return create_error_response(str(e))

def prepare_input_data(s3_event: Dict[str, Any]) -> Dict[str, str]:
    bucket_name = s3_event['bucket']['name']
    encoded_object_key = s3_event['object']['key']
    source_object_key = urllib.parse.unquote_plus(encoded_object_key)
    source_filename = os.path.basename(source_object_key)
    output_object_key = f"{os.environ['OUTPUT_PATH']}{source_filename}"
    uuid = os.path.splitext(source_filename)[0]

    # Get a random target image
    target_key = get_random_image(bucket_name, BASE_IMAGE_PREFIX)

    # Prepare and return the input data dictionary
    return {
        'uuid': uuid,
        'bucket': bucket_name,
        'source': source_object_key,
        'target': target_key,
        'output': output_object_key
    }

def get_random_image(bucket: str, prefix: str) -> str:
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' not in response:
        raise Exception(f"No images found in {prefix}")
    
    images = [obj['Key'] for obj in response['Contents'] if obj['Key'].lower().endswith(('.png'))]
    if not images:
        raise Exception(f"No valid images found in {prefix}")
    
    return random.choice(images)

def invoke_sagemaker_endpoint(input_data: Dict[str, str]) -> None:
    sagemaker_runtime.invoke_endpoint(
        EndpointName=os.environ['SAGEMAKER_ENDPOINT_NAME'],
        ContentType='application/json',
        Body=json.dumps(input_data)
    )

def wait_for_output_file(bucket: str, output_key: str) -> str:
    start_time = time.time()
    
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= MAX_WAIT_TIME:
            raise TimeoutError(f"Output file not found in S3 after {MAX_WAIT_TIME} seconds: {output_key}")
        
        try:
            s3_client.head_object(Bucket=bucket, Key=output_key)
            s3_url = f's3://{bucket}/{output_key}'
            processing_time = round(elapsed_time, 2)  # Round to 2 decimal places
            print(f"Image Processing: Image swapped and upload completed successfully. Processing Time: {processing_time} seconds. Output: {s3_url}")
            return s3_url
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] != '404':
                raise
        time.sleep(CHECK_INTERVAL)

def create_success_response(output_url: str) -> Dict[str, Any]:
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Image Processing: Image swapped and upload completed successfully.',
            'output_url': output_url
        })
    }

def create_error_response(error_message: str) -> Dict[str, Any]:
    return {
        'statusCode': 500,
        'body': json.dumps({'error': error_message})
    }