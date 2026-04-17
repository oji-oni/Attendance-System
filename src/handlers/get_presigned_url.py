import json
import boto3
import os
import uuid
from botocore.config import Config

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

def handler(event, context):
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        upload_type = query_params.get('type', 'attendance') # 'attendance' or 'registration'
        employee_id = query_params.get('employee_id')
        action = query_params.get('action', 'in') # 'in' or 'out'
        
        if upload_type == 'registration':
            bucket = os.environ.get('EMPLOYEE_PROFILE_BUCKET', 'attendance-employee-profiles') # Should be in env
            file_name = f"profiles/{employee_id}.jpg"
        else:
            bucket = os.environ['CAPTURE_BUCKET']
            # Metadata encoded in filename: action_uuid.jpg
            file_name = f"captures/{action}_{uuid.uuid4()}.jpg"

        url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket,
                'Key': file_name,
                'ContentType': 'image/jpeg'
            },
            ExpiresIn=300
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': '*'
            },
            'body': json.dumps({'url': url, 'key': file_name})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Could not generate URL'})
        }
