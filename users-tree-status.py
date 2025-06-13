import pandas as pd
import boto3
from botocore.exceptions import ClientError
def main():
    # Configurar el recurso DynamoDB. Asegúrate de tener configuradas tus credenciales de AWS.
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')  # Cambia la región según corresponda.
    table = dynamodb.Table('fap-users')
    try:
        df = pd.read_excel('users-status.xlsx', header=None)
    except Exception as e:
        print("Error al leer el archivo Excel:", e)
        return
    # Iterar sobre cada fila del DataFrame
    for index, row in df.iterrows():
        idType = "1"
        if row[1] == "CE":
            idType = "2"
        elif row[1] == "NIT":
            idType = "3"
            
        id = idType + str(row[2])
        new_date = row[3] + 'T00:00:00.000'
        status = str(row[4])
        treeStatus = [item.strip() for item in row[5].split(",")]
        try:
            # Obtener el registro por id
            response = table.get_item(Key={'id': id})
        except ClientError as e:
            print(f"Error al obtener el item con id {id}: {e.response['Error']['Message']}")
            continue
        if 'Item' not in response:
            print(f"No se encontró un registro con id {id}.")
            continue
        item = response['Item']
        try:
            # Actualizar la propiedad 'fecha' del registro
            update_response = table.update_item(
                Key={'id': id},
                UpdateExpression="SET vinculationDate = :f, treeStatus = :b, currentStatus = :c",
                ExpressionAttributeValues={':f': str(new_date), ':b': treeStatus, ':c': status },
                ReturnValues="UPDATED_NEW"
            )
            print(f"Registro con id {id} actualizado con nueva fecha {new_date}.")
        except ClientError as e:
            print(f"Error al actualizar el item con id {id}: {e.response['Error']['Message']}")
if __name__ == "__main__":
    main()