import boto3
import json
def extraer_propiedades(bucket_name):
    # Crear el cliente de S3
    s3 = boto3.client('s3')
    
    paginator = s3.get_paginator('list_objects_v2')
    noveltyError = []

    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if key.endswith('.json'):
                try:
                    file_obj = s3.get_object(Bucket=bucket_name, Key=key)
                    content = file_obj['Body'].read().decode('utf-8')
                    data = json.loads(content)
                    
                    records = data.records
                    for record in records:
                        epc = record.get('epc', None)
                        placa = record.get('placa', None)
                        categoria = record.get('categoria', None)
                        estadoSaldo = record.get('estadoSaldo', None)
                        saldoBajo = record.get('categosaldoBajoria', None)
                        numeroCliente = record.get('numeroCliente', None)
                        modalidad = record.get('modalidad', None)
                        estado = record.get('estado', None)
                        saldo = record.get('saldo', None)
                        tid = record.get('tid', None)
                        version = record.get('version', None)
                        codigoIntermediador = record.get('codigoIntermediador', None)
                        
                        if None in (epc, placa, categoria, estadoSaldo, saldoBajo, numeroCliente, modalidad, estado, saldo, tid, version, codigoIntermediador):
                            noveltyError.append({
                                "listName": key,
                                "tid": tid
                            })
                     
                except Exception as e:
                    print(f"Error procesando el archivo {key}: {str(e)}")
if __name__ == '__main__':
    nombre_bucket = 'tu-nombre-de-bucket'
    extraer_propiedades(nombre_bucket)