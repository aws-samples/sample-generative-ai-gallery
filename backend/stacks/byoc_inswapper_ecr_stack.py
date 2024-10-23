from aws_cdk import CfnOutput, Stack, RemovalPolicy
from aws_cdk import aws_ecr as ecr
from constructs import Construct

class ByocInswapperEcrStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an ECR repository
        self.repository = ecr.Repository(self, "ByocInswapperRepository", 
                                         repository_name="byoc-inswapper-repo",
                                         removal_policy=RemovalPolicy.DESTROY,
                                         auto_delete_images=True)
        
        # Outputs
        CfnOutput(self, "ByocInswapperRepositoryUri", value=self.repository.repository_uri, description="The URI of the BYOC Inswapper ECR repository")
        
        CfnOutput(self, "ByocInswapperRepositoryName", value=self.repository.repository_name, description="The name of the BYOC Inswapper ECR repository")
