import boto3
import json

# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='us-east-2')

# Specify the table name
table_name = 'fap-corporate-info'

# Initialize ExclusiveStartKey
exclusive_start_key = None
items = []

while True:
    # Perform a scan on the table with ExclusiveStartKey
    if exclusive_start_key:
        response = dynamodb.scan(TableName=table_name, ExclusiveStartKey=exclusive_start_key)
    else:
        response = dynamodb.scan(TableName=table_name)
    
    # Append scanned items to the list
    items.extend(response['Items'])
    
    # Check if there are more items to scan
    if 'LastEvaluatedKey' in response:
        exclusive_start_key = response['LastEvaluatedKey']
    else:
        break

# Save the scan results to a JSON file
with open('backup-corporate-all.json', 'w') as file:
    json.dump(items, file, indent=4)

print("Scan completed. Data saved to backup.json file.")