from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    aws_apigateway as apigw,
    aws_lambda as lambda_,
    aws_ssm as ssm,
    aws_iam as iam
)
from constructs import Construct
import os

class ApiGatewayApisStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Retrieve S3 bucket name and object path from context
        self.s3_base_bucket_name = self.node.try_get_context("s3_base_bucket_name")
        self.s3_face_images_path = self.node.try_get_context("s3_face_images_path")
        self.ddb_amazon_bedrock_gallery_process_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_process_table_name")
        self.ddb_amazon_bedrock_gallery_display_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_display_table_name")
        self.ddb_amazon_bedrock_gallery_display_history_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_display_history_table_name")
        self.ddb_amazon_bedrock_gallery_base_resource_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_base_resource_table_name")
        self.ddb_amazon_bedrock_user_agreement_table_name = self.node.try_get_context("ddb_amazon_bedrock_user_agreement_table_name")

        # Create API Gateway
        self.api_gateway = self.create_api_gateway()

        # Create API resources: /apis/images/upload
        apis_resource = self.api_gateway.root.add_resource("apis")
        images_resource = apis_resource.add_resource("images")
        self.upload_resource = images_resource.add_resource("upload")

        # Create Lambda function for handling image uploads
        self.upload_image_lambda = self.create_upload_image_lambda_function(
            lambda_path="lambda/apis/put-image", 
            object_path=self.s3_face_images_path
        )

        # Set up Lambda integration for the upload resource
        upload_image_integration = apigw.LambdaIntegration(self.upload_image_lambda)
        
        # Add POST method
        self.upload_resource.add_method(
            "POST",
            upload_image_integration,
            authorization_type=apigw.AuthorizationType.NONE,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True,
                        "method.response.header.Access-Control-Allow-Headers": True,
                        "method.response.header.Access-Control-Allow-Methods": True
                    }
                )
            ]
        )

        # Create API resources: /apis/images/{userId}
        self.get_image_resource = images_resource.add_resource("{userId}")

        # Create Lambda function for handling video generation
        self.get_image_lambda = self.create_get_image_lambda_function(
            lambda_path="lambda/apis/get-image"
        )

        # Set up Lambda integration for the get image resource
        get_image_integration = apigw.LambdaIntegration(self.get_image_lambda)  
        
        # Add GET method
        self.get_image_resource.add_method(
            "GET",
            get_image_integration,
            authorization_type=apigw.AuthorizationType.NONE,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True,
                        "method.response.header.Access-Control-Allow-Headers": True,
                        "method.response.header.Access-Control-Allow-Methods": True
                    }
                )
            ]
        )

        self.user_agreement_lambda = self.create_user_agreement_lambda_function(
            lambda_path="lambda/apis/user-agreement"
        )

        self.user_agreement_api = self.create_user_agreement_api(self.user_agreement_lambda)

        # Output the API Gateway URL as a CloudFormation output
        CfnOutput(
            self, "AmazonBedrockGalleryApiGatewayOutput",
            value=self.api_gateway.url,  # Corrected variable from self.api.url to self.api_gateway.url
            description="The URL of the API Gateway"
        )

    def create_api_gateway(self):
        """Create and return the API Gateway."""
        return apigw.RestApi(
            self, "AmazonBedrockGalleryImageAPI",
            rest_api_name="AmazonBedrockGalleryImageAPI",
            description="This service processes images.",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
            )
        )
    
    def create_user_agreement_api(self, lambda_function):
        """Create and return the User Agreement API Gateway."""
        api = apigw.RestApi(
            self, "AmazonBedrockGalleryUserAgreementAPI",
            rest_api_name="AmazonBedrockGalleryUserAgreementAPI",
            description="This service handles user agreements.",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=apigw.Cors.DEFAULT_HEADERS
            ),
            endpoint_types=[apigw.EndpointType.EDGE],
            deploy=True
        )
        
        agree_resource = api.root.add_resource("agree")
        agree_resource.add_method(
            "POST", 
            apigw.LambdaIntegration(lambda_function),
            authorization_type=apigw.AuthorizationType.NONE,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True,
                        "method.response.header.Access-Control-Allow-Headers": True,
                        "method.response.header.Access-Control-Allow-Methods": True
                    }
                )
            ]
        )
        
        return api

    def create_get_image_lambda_function(self, lambda_path):
        """Create and return a Lambda function with appropriate permissions."""
        lambda_function = lambda_.Function(
            self, "AmazonBedrockGalleryGetImage",
            function_name="AmazonBedrockGalleryGetImage",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset(lambda_path),
            environment={
                "BUCKET_NAME": self.s3_base_bucket_name,
                "DDB_AMAZON_BEDROCK_GALLERY_DISPLAY_TABLE_NAME": self.ddb_amazon_bedrock_gallery_display_table_name
            },
            timeout=Duration.seconds(10),
            memory_size=1024
        )
        
        # Grant permission to put objects in the specified S3 bucket path
        lambda_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[f"arn:aws:s3:::{self.s3_base_bucket_name}/*"]
        ))

        # Grant permission to put items in the specified DDB table
        lambda_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["dynamodb:GetItem", "dynamodb:Query"],
            resources=[
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.ddb_amazon_bedrock_gallery_display_table_name}"
            ]
        ))
        
        return lambda_function

    def create_upload_image_lambda_function(self, lambda_path, object_path):
        """Create and return a Lambda function with appropriate permissions."""
        lambda_function = lambda_.Function(
            self, "AmazonBedrockGalleryUploadImage",
            function_name="AmazonBedrockGalleryUploadImage",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset(lambda_path),
            environment={
                "BUCKET_NAME": self.s3_base_bucket_name,
                "OBJECT_PATH": object_path,
                "DDB_AMAZON_BEDROCK_GALLERY_BASE_RESOURCE_TABLE_NAME": self.ddb_amazon_bedrock_gallery_base_resource_table_name,
                "DDB_AMAZON_BEDROCK_GALLERY_PROCESS_TABLE_NAME": self.ddb_amazon_bedrock_gallery_process_table_name
            },
            timeout=Duration.seconds(10),
            memory_size=1024
        )
        
        # Grant permission to put objects in the specified S3 bucket path
        lambda_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            resources=[
                f"arn:aws:s3:::{self.s3_base_bucket_name}",
                f"arn:aws:s3:::{self.s3_base_bucket_name}/{object_path}*"
            ]
        ))

        # Grant permission to put items in the specified DDB table
        lambda_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:Query"],
            resources=[
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.ddb_amazon_bedrock_gallery_base_resource_table_name}",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.ddb_amazon_bedrock_gallery_process_table_name}"
            ]
        ))
        
        return lambda_function

    def create_user_agreement_lambda_function(self, lambda_path):
        """Create and return a Lambda function for user agreement handling."""
        lambda_function = lambda_.Function(
            self, "UserAgreementLambda",
            function_name="UserAgreementFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_asset(lambda_path),
            environment={
                "DDB_AMAZON_BEDROCK_USER_AGREEMENT_TABLE_NAME": self.ddb_amazon_bedrock_user_agreement_table_name
            },
            timeout=Duration.seconds(10),
            memory_size=1024
        )
        
        # Grant permission to update items in the DynamoDB table
        lambda_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["dynamodb:PutItem", "dynamodb:UpdateItem"],
            resources=[
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.ddb_amazon_bedrock_user_agreement_table_name}"
            ]
        ))
        
        return lambda_function