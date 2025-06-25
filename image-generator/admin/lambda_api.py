import json
import boto3
import os
from botocore.config import Config
from boto3.dynamodb.conditions import Key
from urllib.parse import unquote

# S3 client configuration
s3_config = Config(
    region_name='us-east-1',
    signature_version='s3v4'
)
s3_client = boto3.client('s3', config=s3_config)
bucket_name = 'amazon-bedrock-gallery-global-f0154ca1'
prefix = 'images/base-image/'

# DynamoDB client configuration
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = 'ddb-amazon-bedrock-gallery-base-resource'
table = dynamodb.Table(table_name)

def generate_presigned_url(bucket, key, expiration=3600):
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket,
                                                            'Key': key},
                                                    ExpiresIn=expiration)
        return response
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

def delete_s3_and_dynamodb_data(bucket, key):
    try:
        # Delete image from S3
        s3_client.delete_object(Bucket=bucket, Key=key)
        
        # Delete related metadata from DynamoDB
        filename = os.path.basename(key)
        metadata = filename.replace('.jpeg', '').replace('.jpg', '').replace('.png', '').split('-')
        
        if len(metadata) >= 5:
            historical_period = metadata[0]
            gender = metadata[1]
            skin_tone = metadata[2]
            
            pk = f"#THEME#{historical_period}#GENDER#{gender}#SKIN#{skin_tone}"
            response = table.query(
                KeyConditionExpression=Key('PK').eq(pk)
            )
            
            for item in response.get('Items', []):
                if item.get('base_image_object_key') == key:
                    table.delete_item(
                        Key={
                            'PK': item['PK'],
                            'SK': item['SK']
                        }
                    )
        
        return True
    except Exception as e:
        print(f"Error deleting data: {e}")
        return False

def get_images(event):
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        page = int(query_params.get('page', 1))
        per_page = int(query_params.get('per_page', 12))
        filter_gender = query_params.get('gender', '')
        filter_skin_tone = query_params.get('skin_tone', '')
        filter_profession = query_params.get('profession', '')
        filter_historical_period = query_params.get('historical_period', '')
        filter_artistic_style = query_params.get('artistic_style', '')
        
        # Get image list from S3
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )
        
        images = []
        all_metadata = {
            'genders': set(),
            'skin_tones': set(),
            'professions': set(),
            'historical_periods': set(),
            'artistic_styles': set()
        }
        
        if 'Contents' in response:
            for item in response['Contents']:
                if item['Key'].lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_url = generate_presigned_url(bucket_name, item['Key'])
                    
                    if not image_url:
                        continue
                    
                    filename = os.path.basename(item['Key'])
                    metadata = filename.replace('.jpeg', '').replace('.jpg', '').replace('.png', '').split('-')
                    
                    image_info = {
                        'url': image_url,
                        'key': item['Key'],
                        'metadata': {}
                    }
                    
                    if len(metadata) >= 5:
                        image_info['metadata'] = {
                            'historical_period': metadata[0],
                            'gender': metadata[1],
                            'skin_tone': metadata[2],
                            'profession': metadata[3],
                            'artistic_style': metadata[4]
                        }
                        
                        # Collect metadata for filter options
                        all_metadata['historical_periods'].add(metadata[0])
                        all_metadata['genders'].add(metadata[1])
                        all_metadata['skin_tones'].add(metadata[2])
                        all_metadata['professions'].add(metadata[3])
                        all_metadata['artistic_styles'].add(metadata[4])
                        
                        # Apply filtering
                        if filter_gender and metadata[1] != filter_gender:
                            continue
                        if filter_skin_tone and metadata[2] != filter_skin_tone:
                            continue
                        if filter_profession and metadata[3] != filter_profession:
                            continue
                        if filter_historical_period and metadata[0] != filter_historical_period:
                            continue
                        if filter_artistic_style and metadata[4] != filter_artistic_style:
                            continue
                    
                    images.append(image_info)
        
        # Convert filter options to sorted lists
        filter_options = {
            'genders': sorted(list(all_metadata['genders'])),
            'skin_tones': sorted(list(all_metadata['skin_tones'])),
            'professions': sorted(list(all_metadata['professions'])),
            'historical_periods': sorted(list(all_metadata['historical_periods'])),
            'artistic_styles': sorted(list(all_metadata['artistic_styles']))
        }
        
        # Calculate pagination
        total_images = len(images)
        total_pages = (total_images + per_page - 1) // per_page if total_images > 0 else 1
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_images)
        current_images = images[start_idx:end_idx]
        
        return {
            'success': True,
            'images': current_images,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_images': total_images
            },
            'filter_options': filter_options,
            'current_filters': {
                'gender': filter_gender,
                'skin_tone': filter_skin_tone,
                'profession': filter_profession,
                'historical_period': filter_historical_period,
                'artistic_style': filter_artistic_style
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_image_detail(event):
    try:
        # Extract key from path
        path_params = event.get('pathParameters') or {}
        key = unquote(path_params.get('key', ''))
        
        if not key:
            return {'success': False, 'error': 'No image key provided'}
        
        image_url = generate_presigned_url(bucket_name, key)
        
        if not image_url:
            return {'success': False, 'error': 'Unable to load image'}
        
        filename = os.path.basename(key)
        metadata = filename.replace('.jpeg', '').replace('.jpg', '').replace('.png', '').split('-')
        
        image_info = {
            'url': image_url,
            'key': key,
            'metadata': {}
        }
        
        if len(metadata) >= 5:
            image_info['metadata'] = {
                'historical_period': metadata[0],
                'gender': metadata[1],
                'skin_tone': metadata[2],
                'profession': metadata[3],
                'artistic_style': metadata[4]
            }
        
        return {
            'success': True,
            'image': image_info
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_image(event):
    try:
        # Extract key from path
        path_params = event.get('pathParameters') or {}
        key = unquote(path_params.get('key', ''))
        
        if not key:
            return {'success': False, 'error': 'No image key provided'}
        
        if delete_s3_and_dynamodb_data(bucket_name, key):
            return {
                'success': True,
                'message': 'Image and related metadata have been successfully deleted.'
            }
        else:
            return {
                'success': False,
                'error': 'An error occurred while deleting the image.'
            }
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_multiple(event):
    try:
        body = json.loads(event.get('body', '{}'))
        selected_images = body.get('selected_images', [])
        
        if not selected_images:
            return {
                'success': False,
                'error': 'Please select images to delete.'
            }
        
        success_count = 0
        error_count = 0
        
        for key in selected_images:
            if delete_s3_and_dynamodb_data(bucket_name, key):
                success_count += 1
            else:
                error_count += 1
        
        if error_count == 0:
            message = f'{success_count} images and related metadata have been successfully deleted.'
        else:
            message = f'{success_count} images were deleted, and {error_count} images encountered errors during deletion.'
        
        return {
            'success': True,
            'message': message,
            'success_count': success_count,
            'error_count': error_count
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        # Add CORS headers
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token'
        }
        
        # Handle preflight OPTIONS request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Route requests
        path = event.get('path', '')
        method = event.get('httpMethod', '')
        
        print(f"Processing request: {method} {path}")
        
        if path == '/api/images' and method == 'GET':
            result = get_images(event)
        elif path.startswith('/api/images/') and path != '/api/images/delete-multiple' and method == 'GET':
            result = get_image_detail(event)
        elif path.startswith('/api/images/') and path != '/api/images/delete-multiple' and method == 'DELETE':
            result = delete_image(event)
        elif path == '/api/images/delete-multiple' and method == 'POST':
            result = delete_multiple(event)
        else:
            result = {'success': False, 'error': 'Not found'}
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps(result)
            }
        
        status_code = 200 if result.get('success') else 400
        
        return {
            'statusCode': status_code,
            'headers': headers,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Lambda error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': False, 'error': str(e)})
        }
