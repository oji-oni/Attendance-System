import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', 'GET')
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': '*'
    }

    try:
        if path == '/reports':
            # Simplified report: return all attendance records
            # Real world: Filter by date range
            res = table.scan(
                FilterExpression="begins_with(SK, :sk)",
                ExpressionAttributeValues={":sk": "DATE#"}
            )
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(res['Items'])
            }
            
        elif path == '/employees':
            if method == 'GET':
                res = table.scan(
                    FilterExpression="SK = :sk",
                    ExpressionAttributeValues={":sk": "METADATA"}
                )
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(res['Items'])
                }
        
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Not found'})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
