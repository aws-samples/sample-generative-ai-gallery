#!/usr/bin/env python3
import os
import aws_cdk as cdk

from stacks.byoc.facechain_ecr_stack import ByocFaceChainEcrStack
from stacks.byoc.facechain_codebuild_stack import ByocFaceChainCodeBuildStack
from stacks.facechain.codebuild_trigger_stack import FaceChainCodeBuildTriggerStack
from stacks.facechain.codebuild_status_checker_stack import FaceChainCodeBuildStatusCheckerStack
from stacks.facechain.sagemaker_endpoint_stack import FaceChainSageMakerEndpointStack
from stacks.ddb.tables import DDBTables
from stacks.s3.bucket import S3Bucket
from stacks.apigateway.apis import ApiGatewayApisStack
from stacks.lambdas.image_processing import LambdaImageProcessingStack
from stacks.cognito.userpool import CognitoUserPoolStack

app = cdk.App()

# Byoc Stacks
facechain_ecr_stack = ByocFaceChainEcrStack(app, "ByocFaceChainEcrStack")
facechain_codebuild_stack = ByocFaceChainCodeBuildStack(app, "ByocFaceChainCodeBuildStack", facechain_ecr_stack.repository)

# FaceChain Stacks
facechain_codebuild_trigger_stack = FaceChainCodeBuildTriggerStack(app, "FaceChainCodeBuildTriggerStack", facechain_codebuild_stack.project.project_name)
facechain_codebuild_status_checker_stack = FaceChainCodeBuildStatusCheckerStack(app, "FaceChainCodeBuildStatusCheckerStack",
                                                     codebuild_projects=[
                                                         facechain_codebuild_stack.project.project_name
                                                     ])
facechain_sagemaker_endpoint_stack = FaceChainSageMakerEndpointStack(app, "FaceChainSageMakerEndpointStack",
                                                  facechain_image_uri=f"{facechain_ecr_stack.repository.repository_uri}:latest",
                                                  codebuild_status_resource=facechain_codebuild_status_checker_stack.status_resource)

# DDB Stacks
ddb_tables = DDBTables(app, "DDBTables")

# S3 Stacks
s3_stack = S3Bucket(app, "S3Bucket")

# Create the ApiGateway Stack
api_gateway_apis_stack = ApiGatewayApisStack(app, "AmazonBedrockGalleryApiGatewayStack")

# Create the ImageProcessing Lambda Stack
lambda_image_processing_stack = LambdaImageProcessingStack(app, "AmazonBedrockGalleryLambdaImageProcessingStack")

# Create the Cognito UserPool Stack
cognito_user_pool_stack = CognitoUserPoolStack(app, "AmazonBedrockGalleryCognitoUserPoolStack")

app.synth()
