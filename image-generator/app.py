from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import boto3
import os
from botocore.config import Config
from boto3.dynamodb.conditions import Key

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret key for flash messages

# S3 client configuration - explicit region setting
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

# Generate presigned URL function
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

# Delete image from S3 and metadata from DynamoDB function
def delete_s3_and_dynamodb_data(bucket, key):
    try:
        # Delete image from S3
        s3_client.delete_object(Bucket=bucket, Key=key)
        
        # Delete related metadata from DynamoDB
        # Extract metadata from filename
        filename = os.path.basename(key)
        metadata = filename.replace('.jpeg', '').replace('.jpg', '').replace('.png', '').split('-')
        
        if len(metadata) >= 5:
            historical_period = metadata[0]
            gender = metadata[1]
            skin_tone = metadata[2]
            
            # Find metadata for this image
            pk = f"#THEME#{historical_period}#GENDER#{gender}#SKIN#{skin_tone}"
            response = table.query(
                KeyConditionExpression=Key('PK').eq(pk)
            )
            
            # Delete items with matching object_key
            for item in response.get('Items', []):
                if item.get('base_image_object_key') == key:
                    table.delete_item(
                        Key={
                            'PK': item['PK'],
                            'SK': item['SK']
                        }
                    )
                    print(f"Deleted DynamoDB item: {item['PK']} - {item['SK']}")
        
        return True
    except Exception as e:
        print(f"Error deleting data: {e}")
        return False

# Previous S3 delete function (kept for compatibility)
def delete_s3_image(bucket, key):
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        return True
    except Exception as e:
        print(f"Error deleting image: {e}")
        return False

@app.route('/')
def index():
    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 12))
    
    # Filter parameters
    filter_gender = request.args.get('gender', '')
    filter_skin_tone = request.args.get('skin_tone', '')
    filter_profession = request.args.get('profession', '')
    filter_historical_period = request.args.get('historical_period', '')
    filter_artistic_style = request.args.get('artistic_style', '')
    
    # Get image list from S3 bucket
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
                # Generate presigned URL
                image_url = generate_presigned_url(bucket_name, item['Key'])
                
                if not image_url:
                    continue
                
                # Extract image metadata (from filename)
                filename = os.path.basename(item['Key'])
                metadata = filename.replace('.jpeg', '').replace('.jpg', '').replace('.png', '').split('-')
                
                # Format metadata
                image_info = {
                    'url': image_url,
                    'key': item['Key'],
                    'metadata': {}
                }
                
                # Try to extract metadata from filename
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
    
    return render_template('index.html', 
                          images=current_images, 
                          page=page, 
                          total_pages=total_pages,
                          per_page=per_page,
                          total_images=total_images,
                          filter_options=filter_options,
                          current_filters={
                              'gender': filter_gender,
                              'skin_tone': filter_skin_tone,
                              'profession': filter_profession,
                              'historical_period': filter_historical_period,
                              'artistic_style': filter_artistic_style
                          })

@app.route('/image/<path:key>')
def image_detail(key):
    # Generate presigned URL
    image_url = generate_presigned_url(bucket_name, key)
    
    if not image_url:
        return "Unable to load image.", 404
    
    # Extract metadata from filename
    filename = os.path.basename(key)
    metadata = filename.replace('.jpeg', '').replace('.jpg', '').replace('.png', '').split('-')
    
    image_info = {
        'url': image_url,
        'key': key,
        'metadata': {}
    }
    
    # Try to extract metadata from filename
    if len(metadata) >= 5:
        image_info['metadata'] = {
            'historical_period': metadata[0],
            'gender': metadata[1],
            'skin_tone': metadata[2],
            'profession': metadata[3],
            'artistic_style': metadata[4]
        }
    
    return render_template('detail.html', image=image_info)

@app.route('/delete/<path:key>', methods=['POST'])
def delete_image(key):
    # Delete data from S3 and DynamoDB
    if delete_s3_and_dynamodb_data(bucket_name, key):
        flash('Image and related metadata have been successfully deleted.', 'success')
    else:
        flash('An error occurred while deleting the image.', 'danger')
    
    return redirect(url_for('index'))

@app.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    selected_images = request.form.getlist('selected_images')
    
    if not selected_images:
        flash('Please select images to delete.', 'warning')
        return redirect(url_for('index'))
    
    success_count = 0
    error_count = 0
    
    for key in selected_images:
        if delete_s3_and_dynamodb_data(bucket_name, key):
            success_count += 1
        else:
            error_count += 1
    
    if error_count == 0:
        flash(f'{success_count} images and related metadata have been successfully deleted.', 'success')
    else:
        flash(f'{success_count} images were deleted, and {error_count} images encountered errors during deletion.', 'warning')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
