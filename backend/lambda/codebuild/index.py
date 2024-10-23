import boto3
import os

def handler(event, context):
    codebuild = boto3.client('codebuild')
    
    inswapper_project_name = os.environ['INSWAPPER_PROJECT_NAME']
    gfpgan_project_name = os.environ['GFPGAN_PROJECT_NAME']
    
    # Start both builds in parallel
    inswapper_response = codebuild.start_build(projectName=inswapper_project_name)
    gfpgan_response = codebuild.start_build(projectName=gfpgan_project_name)
    
    return {
        'InswapperBuildId': inswapper_response['build']['id'],
        'GfpganBuildId': gfpgan_response['build']['id']
    }