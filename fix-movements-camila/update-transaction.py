import boto3
import pandas as pd
import csv

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table_movements_detail = dynamodb.Table('fap-movements-detail')

df = pd.read_csv('input.csv', delimiter=';')

updated_records = []

for index, row in df.iterrows():
    accountId = row['accountId']
    dateTransaction = row['dateTransaction']
    dateTransactionNew = row['dateTransactionNew']
    processDate1 = row['processDate1']
    processDate2 = row['processDate2']

    response = table_movements_detail.query(
        IndexName='accountId-processDate-index',
        KeyConditionExpression=boto3.dynamodb.conditions.Key('accountId').eq(str(accountId)) & 
                               boto3.dynamodb.conditions.Key('processDate').between(processDate1, processDate2)
    )

    items = response['Items']
    target_item = next((item for item in items if item['dateTransaction'] == dateTransaction), None)

    if target_item:
        partitionKey = target_item['partitionKey']
        sortKey = target_item['sortKey']

        table_movements_detail.update_item(
            Key={
                'partitionKey': partitionKey,
                'sortKey': sortKey
            },
            UpdateExpression="set dateTransaction = :newDateTransaction",
            ExpressionAttributeValues={
                ':newDateTransaction': dateTransactionNew
            }
        )

        updated_records.append({
            'partitionKey': partitionKey,
            'sortKey': sortKey,
            'dateTransaction': dateTransactionNew
        })

with open('updated_records.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['partitionKey', 'sortKey', 'dateTransaction'])
    writer.writeheader()
    for record in updated_records:
        writer.writerow(record)

print("Script ejecutado correctamente y archivo CSV creado.")