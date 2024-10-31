from flask import Flask, request, jsonify
import boto3
from swapper import process as swapper_process
from PIL import Image
import os

app = Flask(__name__)
s3_client = boto3.client('s3')


@app.route('/ping', methods=['GET'])
def ping():
    health = True  # You can implement health check logic here
    status = 200 if health else 404
    return '', status


@app.route('/invocations', methods=['POST'])
def invocations():
    input_data = request.get_json(force=True)

    uuid = input_data['uuid']
    bucket = input_data['bucket']
    source_object_key = input_data['source']
    target_object_key = input_data['target']
    output_object_key = input_data['output']
    source_path = f"/opt/workspace/source/{uuid}.png"
    target_path = f"/opt/workspace/target/{uuid}.png"
    output_path = f"/opt/workspace/output/{uuid}.png"

    fetch_images(bucket, source_object_key, source_path, target_object_key, target_path)

    process_images(source_path, target_path, output_path)

    s3_client.upload_file(output_path, bucket, output_object_key)

    remove_all_files(source_path, target_path, output_path)

    return jsonify(input_data)


def fetch_images(bucket, source_object_key, source_path, target_object_key, target_path):
    print(f"fetch_images called")

    source_image = get_s3_image(bucket, source_object_key)
    target_image = get_s3_image(bucket, target_object_key)

    os.makedirs(os.path.dirname(source_path), exist_ok=True)
    with open(source_path, "wb") as file:
        file.write(source_image)

    # if file is exists in source_path, then print file size
    if os.path.exists(source_path):
        print(f"source_path size: {os.path.getsize(source_path)}")

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "wb") as file:
        file.write(target_image)

    # if file is exists in target_path, then print file size
    if os.path.exists(target_path):
        print(f"target_path size: {os.path.getsize(target_path)}")


def process_images(source_path, target_path, output_path):
    print(f"process_images called")
    print(f"source_path: {source_path}")
    print(f"target_path: {target_path}")
    print(f"output_path: {output_path}")    

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 이미지 열기
    source_img = Image.open(source_path)
    target_img = Image.open(target_path)

    # 모델 경로 설정
    model_path = "/opt/program/inswapper/checkpoints/inswapper_128.onnx"

    # process 함수 호출
    result_image = swapper_process(source_img, target_img, model_path)

    # 결과 이미지 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_image.save(output_path)


def remove_all_files(source_path, target_path, output_path):
    os.remove(source_path)
    os.remove(target_path)
    os.remove(output_path)


def get_s3_image(s3_bucket, object_key):
    # Retrieve the image from S3 into memory
    print(f"get_s3_image: {s3_bucket}/{object_key}")
    response = s3_client.get_object(Bucket=s3_bucket, Key=object_key)
    return response['Body'].read()
