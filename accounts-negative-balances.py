import pandas as pd
import boto3
from botocore.exceptions import ClientError
def main():
    # Configurar el recurso DynamoDB. Asegúrate de tener configuradas tus credenciales de AWS.
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')  # Cambia la región según corresponda.
    table = dynamodb.Table('fap-accounts')
    # Leer el archivo Excel.
    # Se asume que el archivo "archivo.xlsx" tiene dos columnas:
    #   Columna 1: id (clave primaria para la tabla DynamoDB)
    #   Columna 2: fecha a actualizar en el registro
    try:
        df = pd.read_excel('accounts-balances.xlsx', header=None)
    except Exception as e:
        print("Error al leer el archivo Excel:", e)
        return
    # Iterar sobre cada fila del DataFrame
    for index, row in df.iterrows():
        account_id = row[0]  # Primer columna: id
        datePart = row[1].split('/')
        new_fecha = datePart[2] +'-' + datePart[1] + '-' + datePart[0]   # Segunda columna: nueva fecha
        try:
            # Obtener el registro por id
            response = table.get_item(Key={'accountId': account_id})
        except ClientError as e:
            print(f"Error al obtener el item con id {account_id}: {e.response['Error']['Message']}")
            continue
        if 'Item' not in response:
            print(f"No se encontró un registro con id {account_id}.")
            continue
        item = response['Item']
        # Obtener el valor de amount. Se asume que si no existe, se considera 0.
        balance = item.get('balance')
        try:
            balance_value = float(balance)
        except ValueError:
            print(f"El valor de amount para el id {account_id} no es un número válido.")
            continue
        if balance_value < 0:
            try:
                # Actualizar la propiedad 'fecha' del registro
                update_response = table.update_item(
                    Key={'accountId': account_id},
                    UpdateExpression="SET negativeBalanceDate = :f, negativeBalance = :b",
                    ExpressionAttributeValues={':f': str(new_fecha), ':b': True },  # Se convierte a string; ajusta según tu formato de fecha
                    ReturnValues="UPDATED_NEW"
                )
                print(f"Registro con id {account_id} actualizado con nueva fecha {new_fecha}.")
            except ClientError as e:
                print(f"Error al actualizar el item con id {account_id}: {e.response['Error']['Message']}")
        else:
            print(f"Registro con id {account_id} tiene amount = {balance_value}. No se realiza actualización.")
if __name__ == "__main__":
    main()