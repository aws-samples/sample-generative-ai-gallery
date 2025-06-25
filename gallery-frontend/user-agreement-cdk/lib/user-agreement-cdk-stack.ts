import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ddb from 'aws-cdk-lib/aws-dynamodb';
import * as apigw from 'aws-cdk-lib/aws-apigateway';

export class UserAgreementCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);


    const table = new ddb.Table(this, `ReInventUserAgreementTable`, {
      partitionKey: { name: 'id', type: ddb.AttributeType.STRING },
      sortKey: { name: 'savedAt', type: ddb.AttributeType.STRING },
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    const userAgreementFunction = new lambda.Function(this, `ReInventUserAgreementFunction`, {
      runtime: lambda.Runtime.NODEJS_20_X,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'index.handler',
      environment: {
        TABLE_NAME: table.tableName,
      },
      reservedConcurrentExecutions: 20
    });

    // const prodAlias = new lambda.Alias(this, 'ProdAlias', {
    //   aliasName: 'prod',
    //   version: userAgreementFunction.currentVersion,
    //   provisionedConcurrentExecutions: 2
    // });

    table.grantReadWriteData(userAgreementFunction);

    const api = new apigw.LambdaRestApi(this, 'ReInventUserAgreementApi', {
      handler: userAgreementFunction, 
      defaultCorsPreflightOptions: {
        allowOrigins: apigw.Cors.ALL_ORIGINS,
        allowMethods: apigw.Cors.ALL_METHODS,
        allowHeaders: apigw.Cors.DEFAULT_HEADERS
      },
      endpointConfiguration: {
        types: [apigw.EndpointType.EDGE],
      },
      proxy: false,      
    });

    const agreementResource = api.root.addResource('agree');
    agreementResource.addMethod('POST', new apigw.LambdaIntegration(userAgreementFunction));
  }
}
