#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.byoc_roop_ecr_stack import ByocRoopEcrStack
from stacks.byoc_roop_codebuild_stack import ByocRoopCodeBuildStack
from stacks.byoc_gfpgan_ecr_stack import ByocGfpganEcrStack
from stacks.byoc_gfpgan_codebuild_stack import ByocGfpganCodeBuildStack
from stacks.codebuild_trigger_stack import CodeBuildTriggerStack
from stacks.codebuild_status_checker_stack import CodeBuildStatusCheckerStack
from stacks.sagemaker_endpoint_stack import SageMakerEndpointStack
from stacks.image_processing_lambda_stack import ImageProcessingLambdaStack
from stacks.api_gateway_stack import ApiGatewayStack

app = cdk.App()

# Create the ECR repository for BYOC Roop stack
byoc_roop_ecr_stack = ByocRoopEcrStack(app, "ByocRoopEcrStack")

# Create the CodeBuild for BYOC Roop stack
byoc_roop_codebuild_stack = ByocRoopCodeBuildStack(app, "ByocRoopCodeBuildStack", repository=byoc_roop_ecr_stack.repository)

# Create the ECR repository for BYOC GFPGAN stack
byoc_gfpgan_ecr_stack = ByocGfpganEcrStack(app, "ByocGfpganEcrStack")

# Create the CodeBuild for BYOC GFPGAN stack
byoc_gfpgan_codebuild_stack = ByocGfpganCodeBuildStack(app, "ByocGfpganCodeBuildStack", repository=byoc_gfpgan_ecr_stack.repository)

# Create the CodeBuild Trigger stack
codebuild_trigger_stack = CodeBuildTriggerStack(app, "CodeBuildTriggerStack",
                                                roop_project_name=byoc_roop_codebuild_stack.project.project_name,
                                                gfpgan_project_name=byoc_gfpgan_codebuild_stack.project.project_name)

# Add dependencies
codebuild_trigger_stack.add_dependency(byoc_roop_codebuild_stack)
codebuild_trigger_stack.add_dependency(byoc_gfpgan_codebuild_stack)

# Create the CodeBuild Status Checker stack
codebuild_status_checker_stack = CodeBuildStatusCheckerStack(app, "CodeBuildStatusCheckerStack",
                                                     codebuild_projects=[
                                                         byoc_roop_codebuild_stack.project.project_name,
                                                         byoc_gfpgan_codebuild_stack.project.project_name
                                                     ])

# Add dependencies
codebuild_status_checker_stack.add_dependency(codebuild_trigger_stack)

# Create the SageMaker Endpoint stack
sagemaker_endpoint_stack = SageMakerEndpointStack(app, "SageMakerEndpointStack",
                                                  roop_image_uri=f"{byoc_roop_ecr_stack.repository.repository_uri}:latest",
                                                  gfpgan_image_uri=f"{byoc_gfpgan_ecr_stack.repository.repository_uri}:latest",
                                                  codebuild_status_resource=codebuild_status_checker_stack.status_resource)

# Add dependency to ensure SageMaker Endpoint is created after the images are built
sagemaker_endpoint_stack.add_dependency(codebuild_status_checker_stack)

# Create the Lambda Functions stack
lambda_functions_stack = ImageProcessingLambdaStack(app, "ImageProcessingLambdaStack",
                                              roop_endpoint_name=sagemaker_endpoint_stack.roop_endpoint_name,
                                              gfpgan_endpoint_name=sagemaker_endpoint_stack.gfpgan_endpoint_name)

# Add dependency to ensure Lambda Functions are created after the SageMaker Endpoints
lambda_functions_stack.add_dependency(sagemaker_endpoint_stack)

# Create the API Gateway stack
api_gateway_stack = ApiGatewayStack(app, "ApiGatewayStack")

# Add dependency to ensure API Gateway is created after the Lambda Functions
api_gateway_stack.add_dependency(lambda_functions_stack)

app.synth()
