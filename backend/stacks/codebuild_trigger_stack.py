from aws_cdk import Stack, CustomResource
from aws_cdk import custom_resources as cr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

class CodeBuildTriggerStack(Stack):
    def __init__(self, scope: Construct, id: str, roop_project_name: str, gfpgan_project_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a Lambda function to trigger both CodeBuild projects in parallel
        trigger_lambda = lambda_.Function(self, "TriggerLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda/codebuild"),
            environment={
                "ROOP_PROJECT_NAME": roop_project_name,
                "GFPGAN_PROJECT_NAME": gfpgan_project_name
            }
        )

        # Grant permissions to start builds
        trigger_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["codebuild:StartBuild"],
            resources=["*"]  # You might want to restrict this to specific project ARNs
        ))

        # Create a Custom Resource that uses the Lambda function
        CustomResource(self, "TriggerBuilds",
            service_token=cr.Provider(self, "TriggerBuildsProvider",
                on_event_handler=trigger_lambda
            ).service_token
        )