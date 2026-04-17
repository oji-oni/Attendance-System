import json
import boto3
import os
from datetime import datetime

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
COLLECTION_ID = os.environ['COLLECTION_ID']

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # Registration Flow
        if bucket == os.environ.get('EMPLOYEE_PROFILE_BUCKET'):
            employee_id = key.split('/')[-1].split('.')[0]
            print(f"Registering employee: {employee_id}")
            rekognition.index_faces(
                CollectionId=COLLECTION_ID,
                Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                ExternalImageId=employee_id,
                DetectionAttributes=['ALL']
            )
            # Add to Employee list in DDB
            table.put_item(Item={
                'PK': f"EMP#{employee_id}",
                'SK': 'METADATA',
                'employee_id': employee_id,
                'registered_at': datetime.utcnow().isoformat()
            })
            continue

        # Attendance Flow
        if bucket == os.environ['CAPTURE_BUCKET']:
            # key is captures/in_uuid.jpg
            action = key.split('/')[-1].split('_')[0] # 'in' or 'out'
            
            response = rekognition.search_faces_by_image(
                CollectionId=COLLECTION_ID,
                Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                MaxFaces=1,
                FaceMatchThreshold=90
            )
            
            if not response['FaceMatches']:
                print("No face match found.")
                continue
                
            match = response['FaceMatches'][0]
            employee_id = match['Face']['ExternalImageId']
            confidence = match['Similarity']
            
            print(f"Matched employee {employee_id} with {confidence}% confidence")
            update_attendance(employee_id, action)

def update_attendance(employee_id, action):
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.isoformat()
    
    pk = f"EMP#{employee_id}"
    sk = f"DATE#{date_str}"
    
    if action == 'in':
        # Default status logic
        status = 'present'
        if now.hour >= 9: # Late after 9 AM
            status = 'late'
            
        table.update_item(
            Key={'PK': pk, 'SK': sk},
            UpdateExpression="SET clock_in = if_not_exists(clock_in, :val), #s = if_not_exists(#s, :status)",
            ExpressionAttributeValues={
                ':val': time_str,
                ':status': status
            },
            ExpressionAttributeNames={
                '#s': 'status'
            }
        )
    else:
        table.update_item(
            Key={'PK': pk, 'SK': sk},
            UpdateExpression="SET clock_out = :val",
            ExpressionAttributeValues={':val': time_str}
        )
