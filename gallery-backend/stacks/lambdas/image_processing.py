from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    Size,
    aws_apigateway as apigw,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_events,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_s3 as s3,
    RemovalPolicy,
    aws_s3_notifications as s3n,
    CustomResource,
)
from constructs import Construct
from aws_cdk.custom_resources import Provider

class LambdaImageProcessingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.ddb_amazon_bedrock_gallery_process_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_process_table_name")
        self.ddb_amazon_bedrock_gallery_display_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_display_table_name")
        self.s3_base_bucket_name = self.node.try_get_context("s3_base_bucket_name")
        self.s3_face_images_path = self.node.try_get_context("s3_face_images_path")
        self.s3_face_cropped_images_path = self.node.try_get_context("s3_face_cropped_images_path")
        self.s3_face_swapped_images_path = self.node.try_get_context("s3_face_swapped_images_path")
        self.s3_result_images_path = self.node.try_get_context("s3_result_images_path")
        self.facechain_sagemaker_endpoint_name = self.node.try_get_context("facechain_sagemaker_endpoint_name")

        # Create the face crop Lambda function
        self.face_crop_lambda = self.create_face_crop_lambda()

        # Create the face swap Lambda function
        self.face_swap_lambda = self.create_face_swap_lambda()

        # Create the face swap completion Lambda function
        self.face_swap_completion_lambda = self.create_face_swap_completion_lambda()
        
        # Configure S3 notifications after all Lambda functions are created
        self.configure_s3_notifications()

    def create_face_crop_lambda(self):
        # Create the necessary layers
        pillow_layer_arn = self.node.try_get_context("pillow_layer_arn")
        pillow_layer = lambda_.LayerVersion.from_layer_version_arn(
            self, "PillowLayer",
            layer_version_arn=pillow_layer_arn
        )

        numpy_layer_arn = self.node.try_get_context("numpy_layer_arn")
        numpy_layer = lambda_.LayerVersion.from_layer_version_arn(
            self, "NumpyLayer",
            layer_version_arn=numpy_layer_arn
        )

        # Create the face-crop Lambda function inline
        lambda_func = lambda_.Function(
            self, "AmazonBedrockGalleryFaceCropLambda",
            function_name="AmazonBedrockGalleryFaceCropLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset("lambda/image-processing/face-crop"),
            environment={
                "BUCKET_NAME": self.s3_base_bucket_name,
                "FACE_CROPPED_OBJECT_PATH": self.s3_face_cropped_images_path
            },
            timeout=Duration.seconds(10),
            memory_size=1024,
            layers=[pillow_layer, numpy_layer]
        )

        # Grant permissions for S3 object put/get operations
        lambda_func.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
            resources=[
                f"arn:aws:s3:::{self.s3_base_bucket_name}",
                f"arn:aws:s3:::{self.s3_base_bucket_name}/{self.s3_face_cropped_images_path}*",
                f"arn:aws:s3:::{self.s3_base_bucket_name}/{self.s3_face_images_path}*"
            ]
        ))

        # Grant permissions to invoke Rekognition APIs
        lambda_func.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["rekognition:DetectFaces", "rekognition:DetectLabels"],
            resources=["*"]
        ))

        return lambda_func

    def create_face_swap_lambda(self):
        lambda_func = lambda_.Function(
            self, "AmazonBedrockGalleryFaceSwapLambda",
            function_name="AmazonBedrockGalleryFaceSwapLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset("lambda/image-processing/face-swap"),
            environment={
                "BUCKET_NAME": self.s3_base_bucket_name,
                "RESULT_OBJECT_PATH": self.s3_result_images_path,
                "FACECHAIN_SAGEMAKER_ENDPOINT_NAME": self.facechain_sagemaker_endpoint_name,
                "DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME": self.ddb_amazon_bedrock_gallery_process_table_name
            },
            timeout=Duration.seconds(60),
            memory_size=1024
        )

        # Grant permissions for DynamoDB operations
        lambda_func.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["dynamodb:GetItem", "dynamodb:Query"],
            resources=[
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.ddb_amazon_bedrock_gallery_process_table_name}"
            ]
        ))

        # Grant SageMaker endpoint invoke permission
        lambda_func.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["sagemaker:InvokeEndpoint"],
            resources=[
                f"arn:aws:sagemaker:{self.region}:{self.account}:endpoint/{self.facechain_sagemaker_endpoint_name}"
            ]
        ))

        # Grant permissions for S3 object put/get operations
        lambda_func.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
            resources=[
                f"arn:aws:s3:::{self.s3_base_bucket_name}",
                f"arn:aws:s3:::{self.s3_base_bucket_name}/{self.s3_face_cropped_images_path}*",
                f"arn:aws:s3:::{self.s3_base_bucket_name}/{self.s3_face_swapped_images_path}*"
            ]
        ))

        return lambda_func

    def create_face_swap_completion_lambda(self):
        lambda_func = lambda_.Function(
            self, "AmazonBedrockGalleryFaceSwapCompletionLambda",
            function_name="AmazonBedrockGalleryFaceSwapCompletionLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset("lambda/image-processing/face-swap-completion"),
            environment={
                "DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME": self.ddb_amazon_bedrock_gallery_process_table_name,
                "DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME": self.ddb_amazon_bedrock_gallery_display_table_name
            },
            timeout=Duration.seconds(60),
            memory_size=1024
        )

        # Grant permissions for DynamoDB operations
        lambda_func.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "dynamodb:PutItem", 
                "dynamodb:UpdateItem",
                "dynamodb:Query",
                "dynamodb:GetItem"
            ],
            resources=[
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.ddb_amazon_bedrock_gallery_process_table_name}",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.ddb_amazon_bedrock_gallery_process_table_name}/index/*",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.ddb_amazon_bedrock_gallery_display_table_name}",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.ddb_amazon_bedrock_gallery_display_table_name}/index/*"
            ]
        ))

        # Grant permissions for S3 bucket and object operations
        lambda_func.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            resources=[
                f"arn:aws:s3:::{self.s3_base_bucket_name}",
                f"arn:aws:s3:::{self.s3_base_bucket_name}/*"
            ]
        ))

        return lambda_func

    def configure_s3_notifications(self):
        # Granting Permissions to Lambda Function (Using Unique ID to Avoid Name Collisions)
        self.face_crop_lambda.add_permission(
            "S3InvokeFaceCrop-" + self.node.addr,
            principal=iam.ServicePrincipal("s3.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=f"arn:aws:s3:::{self.s3_base_bucket_name}"
        )
        
        self.face_swap_lambda.add_permission(
            "S3InvokeFaceSwap-" + self.node.addr,
            principal=iam.ServicePrincipal("s3.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=f"arn:aws:s3:::{self.s3_base_bucket_name}"
        )
        
        self.face_swap_completion_lambda.add_permission(
            "S3InvokeFaceCompletion-" + self.node.addr,
            principal=iam.ServicePrincipal("s3.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=f"arn:aws:s3:::{self.s3_base_bucket_name}"
        )
        
        # Create bucket reference
        bucket = s3.Bucket.from_bucket_name(
            self,
            "NotificationsBucket",
            bucket_name=self.s3_base_bucket_name
        )
        
        # Use low-level CustomResource to configure S3 notifications
        configure_notifications_lambda = lambda_.Function(
            self, 
            "ConfigureS3NotificationsLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
import boto3
import cfnresponse
import json

def handler(event, context):
    props = event['ResourceProperties']
    bucket_name = props['BucketName']
    notification_config = {
        'LambdaFunctionConfigurations': [
            {
                'Events': ['s3:ObjectCreated:Put'],
                'LambdaFunctionArn': props['FaceCropLambdaArn'],
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {
                                'Name': 'prefix',
                                'Value': props['FaceImagesPath']
                            }
                        ]
                    }
                }
            },
            {
                'Events': ['s3:ObjectCreated:Put'],
                'LambdaFunctionArn': props['FaceSwapLambdaArn'],
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {
                                'Name': 'prefix',
                                'Value': props['FaceCroppedImagesPath'] 
                            }
                        ]
                    }
                }
            },
            {
                'Events': ['s3:ObjectCreated:Put'],
                'LambdaFunctionArn': props['FaceSwapCompletionLambdaArn'],
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {
                                'Name': 'prefix',
                                'Value': props['ResultImagesPath']
                            }
                        ]
                    }
                }
            }
        ]
    }
    
    if event['RequestType'] in ['Create', 'Update']:
        try:
            s3 = boto3.client('s3')
            s3.put_bucket_notification_configuration(
                Bucket=bucket_name,
                NotificationConfiguration=notification_config
            )
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
        except Exception as e:
            print(f"Error configuring bucket notifications: {str(e)}")
            cfnresponse.send(event, context, cfnresponse.FAILED, {'Error': str(e)})
    elif event['RequestType'] == 'Delete':
        try:
            s3 = boto3.client('s3')
            s3.put_bucket_notification_configuration(
                Bucket=bucket_name,
                NotificationConfiguration={}
            )
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
        except Exception as e:
            print(f"Error clearing bucket notifications: {str(e)}")
            cfnresponse.send(event, context, cfnresponse.FAILED, {'Error': str(e)})
        """),
            timeout=Duration.seconds(30)
        )
        
        # Add S3 permissions
        configure_notifications_lambda.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:PutBucketNotification", "s3:GetBucketNotification"],
            resources=[f"arn:aws:s3:::{self.s3_base_bucket_name}"]
        ))
        
        # Create custom resource provider
        provider = Provider(
            self,
            "S3NotificationsProvider",
            on_event_handler=configure_notifications_lambda
        )

        CustomResource(
            self,
            "S3NotificationsConfig",
            service_token=provider.service_token,
            properties={
                "BucketName": self.s3_base_bucket_name,
                "FaceCropLambdaArn": self.face_crop_lambda.function_arn,
                "FaceSwapLambdaArn": self.face_swap_lambda.function_arn,
                "FaceSwapCompletionLambdaArn": self.face_swap_completion_lambda.function_arn,
                "FaceImagesPath": self.s3_face_images_path,
                "FaceCroppedImagesPath": self.s3_face_cropped_images_path,
                "ResultImagesPath": self.s3_result_images_path
            }
        )
