import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 1. Get all employees
    # In a real system, we'd use a GSI or a separate table.
    # Here we scan for PK starting with EMP# and SK = METADATA
    response = table.scan(
        FilterExpression="SK = :sk",
        ExpressionAttributeValues={":sk": "METADATA"}
    )
    employees = response['Items']
    
    for emp in employees:
        emp_id = emp['employee_id']
        pk = f"EMP#{emp_id}"
        sk = f"DATE#{date_str}"
        
        # Check if record exists for today
        res = table.get_item(Key={'PK': pk, 'SK': sk})
        
        if 'Item' not in res:
            # Mark as absent
            table.put_item(Item={
                'PK': pk,
                'SK': sk,
                'status': 'absent',
                'marked_at': datetime.utcnow().isoformat()
            })
            print(f"Marked {emp_id} as absent.")
