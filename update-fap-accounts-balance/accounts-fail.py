import boto3
import pandas as pd

def scan_dynamodb_table():
    session = boto3.Session()
    dynamodb = session.resource('dynamodb', region_name='us-east-2')

    table = dynamodb.Table('fap-accounts')

    last_evaluated_key = None
    items = []

    while True:
        if last_evaluated_key:
            response = table.scan(
                FilterExpression='attribute_not_exists(balanceStatus)',
                ExclusiveStartKey=last_evaluated_key
            )
        else:
            response = table.scan(
                FilterExpression='attribute_not_exists(balanceStatus)'
            )
        
        items.extend(response.get('Items', []))
        
        last_evaluated_key = response.get('LastEvaluatedKey')
        
        if not last_evaluated_key:
            break

    return items

def save_to_csv(items, filename):
    df = pd.DataFrame(items)
    
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    results = scan_dynamodb_table()
    save_to_csv(results, 'fap_accounts_without_balanceStatus.csv')
    print(f"Items without 'balanceStatus' have been saved to 'fap_accounts_without_balanceStatus.csv'")