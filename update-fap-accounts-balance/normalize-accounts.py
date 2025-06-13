import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

accounts_table = dynamodb.Table('fap-accounts')
vehicles_table = dynamodb.Table('fap-vehicles')
max_category_vehicle = None

with open('parameters.json', 'r') as f:
    external_data = json.load(f)

def scan_accounts():
    items = []
    response = accounts_table.scan()
    items.extend(response.get('Items', []))
    
    while 'LastEvaluatedKey' in response:
        response = accounts_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    return items

def query_vehicles(account_id):
    items = []
    last_evaluated_key = None

    while True:
        query_params = {
            'IndexName': 'account-index',
            'KeyConditionExpression': 'account = :a AND currentStatus = :cs',
            'FilterExpression': '#s = :s',
            'ExpressionAttributeNames': {
                '#s': 'state'
            },
            'ExpressionAttributeValues': {
                ':a': str(account_id),
                ':cs': "1",
                ':s': 2
            }
        }

        if last_evaluated_key:
            query_params['ExclusiveStartKey'] = last_evaluated_key

        response = vehicles_table.query(**query_params)

        items.extend(response['Items'])

        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break

    return items


def get_max_category_value(vehicles):
    print(f"vehicles>> {vehicles}")
    if len(vehicles) > 0:
        return max(vehicle['categoryValue'] for vehicle in vehicles)
    return "1"

def get_external_item(category_value):
    for item in external_data["items"]:
        if int(item['value']) == int(category_value):
            return item
    return None

def create_update_object(account, external_item):
    balance = int(account['balance'])
    minimum_balance = int(external_item['minimumBalance'])
    if account.get('activeLowBalance', False) or account.get('migration', False):
        print(f"active low balance>> {account}")
        low_balance = int(account['balanceLow'])
    else:
        low_balance = int(external_item['lowBalance'])
    
    if balance > low_balance:
        return {'lowBalance': 0, 'balanceStatus': 1}
    elif balance <= low_balance and balance > minimum_balance:
        return {'lowBalance': 1, 'balanceStatus': 3}
    else:
        return {'lowBalance': 0, 'balanceStatus': 2}


def update_account(account, update_obj, updateCategory):
    update_expression = 'SET stateLowBalance = :alb, stateBalance = :bs'
    expression_attribute_values = {
        ':alb': update_obj['lowBalance'],
        ':bs': update_obj['balanceStatus']
    }
    if updateCategory is not None:
        update_expression += ', maxCategoryVehicle = :mcv'
        expression_attribute_values[':mcv'] = updateCategory

    if account.get('nure', None) is None:
        update_expression += ', nure = :nure'
        expression_attribute_values[':nure'] = " "
        
    
    accounts_table.update_item(
        Key={'accountId': int(account['accountId'])},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values
    )
    print(f"update account>> {account['accountId']}")

def main():
    accounts = scan_accounts()
    for account in accounts:
        print(f"account>>> {account}")
        account_id = account['accountId']
        updateCategory = None
        if account.get('maxCategoryVehicle') is None:
            print("search vehicles")
            vehicles = query_vehicles(account_id)
            max_category_vehicle = get_max_category_value(vehicles)
            updateCategory = max_category_vehicle
        else:
            max_category_vehicle = account['maxCategoryVehicle']

        external_item = get_external_item(max_category_vehicle)
        if external_item:
            update_obj = create_update_object(account, external_item)
            update_account(account, update_obj, updateCategory)

if __name__ == '__main__':
    main()