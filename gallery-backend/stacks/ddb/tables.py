from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
)
from constructs import Construct
import os

class DDBTables(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.ddb_amazon_bedrock_gallery_process_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_process_table_name")
        self.ddb_amazon_bedrock_gallery_display_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_display_table_name")
        self.ddb_amazon_bedrock_gallery_display_history_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_display_history_table_name")
        self.ddb_amazon_bedrock_gallery_base_resource_table_name = self.node.try_get_context("ddb_amazon_bedrock_gallery_base_resource_table_name")
        self.ddb_amazon_bedrock_user_agreement_table_name = self.node.try_get_context("ddb_amazon_bedrock_user_agreement_table_name")
        
        self.ddb_amazon_bedrock_gallery_process_table = dynamodb.Table(
            self, 'AmazonBedrockGalleryProcessTable',
                table_name=self.ddb_amazon_bedrock_gallery_process_table_name,
                partition_key=dynamodb.Attribute(
                    name='PK', #UUID#{uuid}
                    type=dynamodb.AttributeType.STRING
                ),
                removal_policy=RemovalPolicy.DESTROY,
                billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        
        self.ddb_amazon_bedrock_gallery_display_table = dynamodb.Table(
                self, 'AmazonBedrockGalleryDisplayTable',
                table_name=self.ddb_amazon_bedrock_gallery_display_table_name,
                partition_key=dynamodb.Attribute(
                    name='PK', #USERID#{user_id}
                    type=dynamodb.AttributeType.STRING
                ),
                removal_policy=RemovalPolicy.DESTROY,
                billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            )

        self.ddb_amazon_bedrock_gallery_display_history_table = dynamodb.Table(
                self, 'AmazonBedrockGalleryDisplayHistoryTable',
                table_name=self.ddb_amazon_bedrock_gallery_display_history_table_name,
                partition_key=dynamodb.Attribute(
                    name='PK', #UUID#{uuid}
                    type=dynamodb.AttributeType.STRING
                ),
                removal_policy=RemovalPolicy.DESTROY,
                billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            )

        self.ddb_amazon_bedrock_gallery_base_resource_table = dynamodb.Table(
            self, 'AmazonBedrockGalleryBaseResourceTable',
            table_name=self.ddb_amazon_bedrock_gallery_base_resource_table_name,
            partition_key=dynamodb.Attribute(
                name='PK',  #THEME#{theme}#GENDER#{gender}#SKIN#{skin}
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='SK',  #UUID#{uuid}
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        self.ddb_amazon_bedrock_user_agreement_table = dynamodb.Table(
            self, 'AmazonBedrockUserAgreementTable',
            table_name=self.ddb_amazon_bedrock_user_agreement_table_name,
            partition_key=dynamodb.Attribute(
                name='PK', #USERID#{user_id}#NAME#{name}
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='savedAt',
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        