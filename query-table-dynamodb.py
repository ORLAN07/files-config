import boto3
import csv
import argparse
from boto3.dynamodb.conditions import Key
def query_dynamodb_by_date(table_name, date_key, date_value, region_name='us-east-1'):
    # Create the DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    table = dynamodb.Table(table_name)
    
    items = []
    response = table.query(
        KeyConditionExpression=Key(date_key).eq(date_value)
    )
    items.extend(response.get('Items', []))
    
    # Handle pagination using LastEvaluatedKey
    while response.get('LastEvaluatedKey'):
        response = table.query(
            KeyConditionExpression=Key(date_key).eq(date_value),
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        items.extend(response.get('Items', []))
    
    return items
def write_to_csv(items, output_filename):
    if not items:
        print("No data found to write.")
        return
    # Assume all items have the same keys; use the first item's keys as CSV header.
    fields = items[0].keys()
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(items)
    print(f"Data saved in '{output_filename}'")
if __name__ == '__main__':
    # Query the table for the specified date value
    items = query_dynamodb_by_date('fap-save-balance-history', 'partitionKey', '2023-07-31', 'us-east-2')
    
    # Write the result to a CSV file
    write_to_csv(items, '2023-07-31')


import boto3
import csv

# Configura tus credenciales y región de AWS
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

# Nombre de la tabla y el índice
table = dynamodb.Table('fap-save-balance-history')

# Parámetros iniciales para la consulta
params = {
    'KeyConditionExpression': "#id = :id",
    'ExpressionAttributeNames': {
        "#id": "partitionKey"
    },
    'ExpressionAttributeValues': {
        ":id": "2024-12-30"
    }
}

# Nombre del archivo CSV donde se guardarán los resultados
csv_file = '2023-07-30.csv'

# Crear y escribir en el archivo CSV
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    headers_written = False

    while True:
        response = table.query(**params)
        # Revisar si hay items para extraer las claves
        if response['Items']:
            if not headers_written:
                # Extraer las claves del primer item para usarlas como cabeceras de columnas
                headers = list(response['Items'][0].keys())
                writer.writerow(headers)
                headers_written = True
            # Escribe los datos
            for item in response['Items']:
                # Escribir los valores de cada item basado en las cabeceras
                row = [item.get(header, '') for header in headers]
                writer.writerow(row)

        # Verificar si hay más páginas
        if 'LastEvaluatedKey' in response:
            params['ExclusiveStartKey'] = response['LastEvaluatedKey']
        else:
            break

print("Datos guardados en:", csv_file)


scp -i ~/.ssh/carroya_instance_key ubuntu@10.156.5.207:/home/ubuntu/scripts/dynamodb/web-tags-paid.csv /Users/orlando.rubio/Documents/