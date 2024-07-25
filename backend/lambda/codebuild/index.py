import boto3
import os

def handler(event, context):
    codebuild = boto3.client('codebuild')
    
    roop_project_name = os.environ['ROOP_PROJECT_NAME']
    gfpgan_project_name = os.environ['GFPGAN_PROJECT_NAME']
    
    # Start both builds in parallel
    roop_response = codebuild.start_build(projectName=roop_project_name)
    gfpgan_response = codebuild.start_build(projectName=gfpgan_project_name)
    
    return {
        'RoopBuildId': roop_response['build']['id'],
        'GfpganBuildId': gfpgan_response['build']['id']
    }