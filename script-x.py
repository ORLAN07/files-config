import boto3
import csv

# Configura tus credenciales y región de AWS
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

# Nombre de la tabla y el índice
table = dynamodb.Table('fap-commons-pro-list-info')

# Parámetros iniciales para la consulta
params = {
    'KeyConditionExpression': "#id = :id",
    'ExpressionAttributeNames': {
        "#id": "id"
    },
    'ExpressionAttributeValues': {
        ":id": "2024-05-22"
    }
}

# Nombre del archivo CSV donde se guardarán los resultados
csv_file = 'backup-list-info.csv'

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




#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import boto3
import csv

# Specify your DynamoDB table name
table_name = 'fap-movements-detail'

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table(table_name)
csv_file_path = 'trx_corregidas.csv'
output_csv_path = 'updated_items.csv'

# List to store updated items
updated_items = []

# Step 3: Update 'dateTransaction' attribute in DynamoDB using values from CSV
with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
    # Use DictReader with the specified delimiter and skip the first row (headers)
    reader = csv.DictReader(csvfile, delimiter=';', skipinitialspace=True)

    for row in reader:
        partition_key = row['partitionKey']
        sort_key = row['sortKey']  # Replace with the actual column name for the sort key
        update_expression = 'SET dateTransaction = :new_date'
        expression_values = {':new_date': row['fechacorrecta']}

        # Perform update and retrieve updated item
        response = table.update_item(
            Key={'partitionKey': partition_key, 'sortKey': sort_key},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'  # Return all attributes of the updated item
        )

        # Append the updated item to the list
        updated_items.append(response['Attributes'])

# Save updated items to CSV
with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = updated_items[0].keys()  # Assuming all items have the same attributes
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

    writer.writeheader()
    for item in updated_items:
        writer.writerow(item)

print(f"Updated items saved to {output_csv_path}")