from aws_cdk import CfnOutput, Stack, RemovalPolicy
from aws_cdk import aws_ecr as ecr
from constructs import Construct

class ByocGfpganEcrStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an ECR repository
        self.repository = ecr.Repository(self, "ByocGfpganRepository", 
                                         repository_name="byoc-gfpgan-repo",
                                         removal_policy=RemovalPolicy.DESTROY,
                                         auto_delete_images=True)

        # Outputs
        CfnOutput(self, "ByocGfpganRepositoryUri", value=self.repository.repository_uri, description="The URI of the BYOC GFPGAN ECR repository")
        
        CfnOutput(self, "ByocGfpganRepositoryName", value=self.repository.repository_name, description="The name of the BYOC GFPGAN ECR repository")