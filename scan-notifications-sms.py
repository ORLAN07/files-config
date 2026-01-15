#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para escanear la tabla fap-notifications-center y obtener
notificaciones con SMS activo.

Filtra por:
- status = true
- fanOut.media = "sms"
- sms.status = true

Genera un JSON con notificationType, description y configuración de SMS.

Uso: python3 scan-notifications-sms.py
"""

import boto3
import json
from decimal import Decimal
from botocore.exceptions import ClientError


# Configuración
TABLE_NAME = 'fap-notifications-center'
REGION = 'us-east-2'
OUTPUT_FILE = 'notifications-sms-active.json'


class DecimalEncoder(json.JSONEncoder):
    """
    Helper para convertir Decimal a tipos JSON compatibles.
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)


def scan_notifications_sms(dynamodb_client, table_name):
    """
    Escanea la tabla fap-notifications-center filtrando por status=true
    y fanOut con media="sms" y status=true.
    
    Args:
        dynamodb_client: Cliente de DynamoDB
        table_name (str): Nombre de la tabla
        
    Returns:
        list: Lista de notificaciones que cumplen los criterios
    """
    notifications = []
    
    try:
        # Configurar el scan con filtros
        scan_kwargs = {
            'TableName': table_name,
            'FilterExpression': '#status = :status_val',
            'ExpressionAttributeNames': {
                '#status': 'status'
            },
            'ExpressionAttributeValues': {
                ':status_val': {'BOOL': True}
            }
        }
        
        print(f"🔍 Escaneando tabla {table_name}...")
        print()
        
        # Ejecutar scan con paginación
        scanned_count = 0
        matched_count = 0
        
        while True:
            response = dynamodb_client.scan(**scan_kwargs)
            items = response.get('Items', [])
            scanned_count += len(items)
            
            # Procesar cada item
            for item in items:
                # Verificar si tiene fanOut
                if 'fanOut' in item and 'L' in item['fanOut']:
                    fan_out_list = item['fanOut']['L']
                    
                    for fan_out in fan_out_list:
                        if 'M' in fan_out:
                            fan_out_obj = fan_out['M']
                            
                            # Verificar si media = "sms" y status = true
                            if ('media' in fan_out_obj and 'S' in fan_out_obj['media'] and 
                                fan_out_obj['media']['S'] == 'sms' and
                                'status' in fan_out_obj and 'BOOL' in fan_out_obj['status'] and
                                fan_out_obj['status']['BOOL'] == True):
                                
                                # Extraer datos relevantes
                                notification_data = extract_notification_data(item, fan_out_obj)
                                notifications.append(notification_data)
                                matched_count += 1
                                print(f"✅ Encontrada: {notification_data.get('notificationType', 'N/A')}")
            
            # Verificar si hay más páginas
            if 'LastEvaluatedKey' not in response:
                break
            
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        
        print()
        print(f"📊 Total escaneados: {scanned_count}")
        print(f"✅ Total encontrados con SMS activo: {matched_count}")
        
        return notifications
        
    except ClientError as e:
        print(f"❌ Error al escanear tabla: {e.response['Error']['Message']}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return []


def extract_notification_data(item, fan_out_sms):
    """
    Extrae los datos relevantes de una notificación.
    
    Args:
        item: Item de DynamoDB
        fan_out_sms: Objeto fanOut con media=sms
        
    Returns:
        dict: Datos formateados de la notificación
    """
    notification = {}
    
    # notificationType
    if 'notificationType' in item:
        if 'S' in item['notificationType']:
            notification['notificationType'] = item['notificationType']['S']
        elif 'N' in item['notificationType']:
            notification['notificationType'] = item['notificationType']['N']
    
    # description
    if 'description' in item and 'S' in item['description']:
        notification['description'] = item['description']['S']
    
    # Extraer toda la configuración de SMS del fanOut
    sms_data = {}
    
    for key, value in fan_out_sms.items():
        if 'S' in value:
            sms_data[key] = value['S']
        elif 'N' in value:
            sms_data[key] = value['N']
        elif 'BOOL' in value:
            sms_data[key] = value['BOOL']
        elif 'M' in value:
            # Si es un map, extraer recursivamente
            sms_data[key] = extract_map(value['M'])
        elif 'L' in value:
            # Si es una lista, extraer recursivamente
            sms_data[key] = extract_list(value['L'])
    
    notification['smsConfig'] = sms_data
    
    return notification


def extract_map(map_data):
    """
    Extrae datos de un Map de DynamoDB.
    """
    result = {}
    for key, value in map_data.items():
        if 'S' in value:
            result[key] = value['S']
        elif 'N' in value:
            result[key] = value['N']
        elif 'BOOL' in value:
            result[key] = value['BOOL']
        elif 'M' in value:
            result[key] = extract_map(value['M'])
        elif 'L' in value:
            result[key] = extract_list(value['L'])
    return result


def extract_list(list_data):
    """
    Extrae datos de una List de DynamoDB.
    """
    result = []
    for item in list_data:
        if 'S' in item:
            result.append(item['S'])
        elif 'N' in item:
            result.append(item['N'])
        elif 'BOOL' in item:
            result.append(item['BOOL'])
        elif 'M' in item:
            result.append(extract_map(item['M']))
        elif 'L' in item:
            result.append(extract_list(item['L']))
    return result


def save_to_json(data, output_file):
    """
    Guarda los datos en un archivo JSON.
    
    Args:
        data (list): Datos a guardar
        output_file (str): Nombre del archivo de salida
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, cls=DecimalEncoder)
        
        print()
        print(f"💾 Archivo guardado: {output_file}")
        print(f"📄 Total de notificaciones: {len(data)}")
        
    except Exception as e:
        print(f"❌ Error al guardar archivo: {e}")


def main():
    """
    Función principal del script.
    """
    print("=" * 80)
    print("SCAN NOTIFICACIONES - SMS ACTIVO")
    print("=" * 80)
    print(f"Tabla: {TABLE_NAME}")
    print(f"Región: {REGION}")
    print(f"Filtros: status=true, fanOut.media='sms', sms.status=true")
    print("=" * 80)
    print()
    
    # Inicializar cliente de DynamoDB
    try:
        dynamodb_client = boto3.client('dynamodb', region_name=REGION)
        print(f"✅ Conectado a DynamoDB en región {REGION}")
        print()
    except Exception as e:
        print(f"❌ Error al conectar con DynamoDB: {e}")
        return
    
    # Escanear notificaciones
    notifications = scan_notifications_sms(dynamodb_client, TABLE_NAME)
    
    if not notifications:
        print("⚠️  No se encontraron notificaciones que cumplan los criterios")
        return
    
    # Guardar en JSON
    save_to_json(notifications, OUTPUT_FILE)
    
    # Mostrar resumen
    print()
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Notificaciones encontradas: {len(notifications)}")
    print()
    print("Tipos de notificación:")
    for notif in notifications:
        print(f"  - {notif.get('notificationType', 'N/A')}: {notif.get('description', 'Sin descripción')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
