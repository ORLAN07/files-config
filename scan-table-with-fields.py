import boto3
import csv
def scan_dynamodb(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table(table_name)
    
    done = False
    start_key = None
    items = []
    while not done:
        if start_key:
            response = table.scan(ExclusiveStartKey=start_key)
        else:
            response = table.scan()
        items.extend(response.get('Items', []))
        
        start_key = response.get('LastEvaluatedKey', None)
        if not start_key:
            done = True
    return items
def write_to_csv(items, filename='fap-logins.csv'):
    fieldnames = ['id', 'personId', 'documentNumber', 'documentType', 'names', 'lastNames', 'dataPolicy', 'creationDate', 'phoneNumber', 'email', 'roles', 'status']
    filtered_items = []
    for item in items:
        filtered = { key: item.get(key, '') for key in fieldnames}
        filtered_items.append(filtered)
    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_items)
def main():
    table_name = 'fap-logins'
    
    print(f"Iniciando el scan en la tabla '{table_name}' ...")
    items = scan_dynamodb(table_name)
    print(f"Total de items escaneados: {len(items)}")
    
    write_to_csv(items)
    print("El archivo CSV se ha generado exitosamente.")
if __name__ == '__main__':
    main()