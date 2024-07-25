from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_events,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct
from aws_cdk.aws_s3_deployment import BucketDeployment, Source

class ImageProcessingLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, roop_endpoint_name: str, gfpgan_endpoint_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_base_bucket_name = self.node.try_get_context("s3_base_bucket_name")
        self.s3_bucket_name = f"{s3_base_bucket_name}-{self.account}"
        self.s3_face_images_path = self.node.try_get_context("s3_face_images_path")
        self.s3_masked_face_images_path = self.node.try_get_context("s3_masked_face_images_path")
        self.s3_swapped_face_images_path = self.node.try_get_context("s3_swapped_face_images_path")
        self.s3_result_images_path = self.node.try_get_context("s3_result_images_path")

        self.lambda_role = self.create_lambda_role()
        self.bucket = self.create_s3_bucket()

        self.roop_lambda = self.create_lambda_function("RoopLambdaFunction", "lambda/roop", roop_endpoint_name, self.s3_swapped_face_images_path)
        self.gfpgan_lambda = self.create_lambda_function("GfpganLambdaFunction", "lambda/gfpgan", gfpgan_endpoint_name, self.s3_result_images_path)
        self.face_detection_lambda = self.create_face_detection_lambda()

        self.add_s3_event_sources()
        self.create_outputs()

        self.add_s3_cors_rule()
        self.upload_base_image()

    def create_lambda_role(self):
        return iam.Role(self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )

    def create_lambda_function(self, id, code_path, endpoint_name, output_path):
        return lambda_.Function(self, id,
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset(code_path),
            timeout=Duration.seconds(300),
            memory_size=1024,
            environment={
                "SAGEMAKER_ENDPOINT_NAME": endpoint_name,
                "OUTPUT_PATH": output_path
            },
            role=self.lambda_role
        )

    def create_face_detection_lambda(self):
        current_region = self.region

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

        face_detection_lambda = lambda_.Function(self, "FaceDetectionLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset("lambda/face_detection"),
            timeout=Duration.seconds(300),
            environment={
                "REGION": current_region,
                "OUTPUT_PATH": self.s3_masked_face_images_path
            },
            layers=[pillow_layer, numpy_layer]
        )

        self.bucket.grant_read_write(face_detection_lambda)
        face_detection_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["rekognition:DetectFaces"],
            resources=["*"]
        ))

        return face_detection_lambda

    def create_s3_bucket(self):
        return s3.Bucket(self, "GenAiGalleryBucket",
            bucket_name=self.s3_bucket_name,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
    
    def add_s3_event_sources(self):
        self.add_s3_event_source(self.face_detection_lambda, self.s3_face_images_path)
        self.add_s3_event_source(self.roop_lambda, self.s3_masked_face_images_path)
        self.add_s3_event_source(self.gfpgan_lambda, self.s3_swapped_face_images_path)

    def add_s3_event_source(self, lambda_func, prefix):
        lambda_func.add_event_source(lambda_events.S3EventSource(self.bucket,
            events=[s3.EventType.OBJECT_CREATED],
            filters=[s3.NotificationKeyFilter(prefix=prefix)]
        ))

    def create_outputs(self):
        self.create_lambda_outputs("Roop", self.roop_lambda)
        self.create_lambda_outputs("Gfpgan", self.gfpgan_lambda)
        self.create_lambda_outputs("FaceDetection", self.face_detection_lambda)

    def create_lambda_outputs(self, prefix, lambda_func):
        CfnOutput(self, f"{prefix}LambdaName", value=lambda_func.function_name, description=f"The name of the {prefix} Lambda function")
        CfnOutput(self, f"{prefix}LambdaArn", value=lambda_func.function_arn, description=f"The ARN of the {prefix} Lambda function")



    def add_s3_cors_rule(self):
        self.bucket.add_cors_rule(
            allowed_methods=[s3.HttpMethods.PUT],
            allowed_origins=["*"],
            allowed_headers=["*"],
            max_age=3000
        )


    def upload_base_image(self):
        return BucketDeployment(
            self, 
            "UploadBaseImage", 
            sources=[Source.asset("./assets/images")],
            destination_bucket=self.bucket,
            destination_key_prefix= "images"
        )