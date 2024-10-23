from aws_cdk import Stack, CustomResource
from aws_cdk import aws_sagemaker as sagemaker
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct

class SageMakerEndpointStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, inswapper_image_uri: str, gfpgan_image_uri: str, codebuild_status_resource: CustomResource, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add a dependency on the CodeBuild status resource
        self.node.add_dependency(codebuild_status_resource)
        
        # Create IAM Role for SageMaker
        sagemaker_role = iam.Role(self, "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
            ]
        )

        # Create SageMaker Model for Inswapper
        inswapper_model = sagemaker.CfnModel(self, "InswapperModel",
            execution_role_arn=sagemaker_role.role_arn,
            primary_container={
                "image": inswapper_image_uri,
                "mode": "SingleModel"
            },
            model_name="inswapper-model"
        )

        # Create SageMaker Model for GFPGAN
        gfpgan_model = sagemaker.CfnModel(self, "GfpganModel",
            execution_role_arn=sagemaker_role.role_arn,
            primary_container={
                "image": gfpgan_image_uri,
                "mode": "SingleModel"
            },
            model_name="gfpgan-model"
        )

        # Create SageMaker Endpoint Configuration for Inswapper
        inswapper_endpoint_config = sagemaker.CfnEndpointConfig(self, "InswapperEndpointConfig",
            production_variants=[
                {
                    "initialInstanceCount": 1,
                    "instanceType": "ml.g6.xlarge",
                    "modelName": inswapper_model.model_name,
                    "variantName": "InswapperVariant"
                }
            ],
            endpoint_config_name="inswapper-endpoint-config"
        )
        inswapper_endpoint_config.add_dependency(inswapper_model)

        # Create SageMaker Endpoint Configuration for GFPGAN
        gfpgan_endpoint_config = sagemaker.CfnEndpointConfig(self, "GfpganEndpointConfig",
            production_variants=[
                {
                    "initialInstanceCount": 1,
                    "instanceType": "ml.g6.xlarge",
                    "modelName": gfpgan_model.model_name,
                    "variantName": "GfpganVariant"
                }
            ],
            endpoint_config_name="gfpgan-endpoint-config"
        )
        gfpgan_endpoint_config.add_dependency(gfpgan_model)

        # Create SageMaker Endpoint for Inswapper
        inswapper_endpoint = sagemaker.CfnEndpoint(self, "InswapperEndpoint",
            endpoint_config_name=inswapper_endpoint_config.endpoint_config_name,
            endpoint_name="inswapper-endpoint"
        )
        inswapper_endpoint.add_dependency(inswapper_endpoint_config)

        # Create SageMaker Endpoint for GFPGAN
        gfpgan_endpoint = sagemaker.CfnEndpoint(self, "GfpganEndpoint",
            endpoint_config_name=gfpgan_endpoint_config.endpoint_config_name,
            endpoint_name="gfpgan-endpoint"
        )
        gfpgan_endpoint.add_dependency(gfpgan_endpoint_config)

        # Expose endpoint names as properties
        self.inswapper_endpoint_name = inswapper_endpoint.endpoint_name
        self.gfpgan_endpoint_name = gfpgan_endpoint.endpoint_name