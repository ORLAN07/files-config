#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar cuentas en DynamoDB con fecha de migración.
Lee un CSV con ACCOUNT_ID y migrationDate, consulta la tabla fap-accounts
y actualiza cada registro con la nueva propiedad migrationDate.

Uso: python update-accounts-migration.py
"""

import boto3
import csv
from datetime import datetime
from botocore.exceptions import ClientError


# Configuración
TABLE_NAME = 'fap-accounts'
REGION = 'us-east-2'
CSV_FILE = 'accounts-migration.csv'


def read_csv_accounts(csv_file):
    """
    Lee el archivo CSV y retorna una lista de diccionarios con accountId y migrationDate.
    
    Args:
        csv_file (str): Ruta al archivo CSV
        
    Returns:
        list: Lista de diccionarios con datos de cuentas
    """
    accounts = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Verificar que el CSV tenga las columnas necesarias
            if 'accountId' not in reader.fieldnames or 'migrationDate' not in reader.fieldnames:
                raise ValueError("El CSV debe tener las columnas 'accountId' y 'migrationDate'")
            
            for row in reader:
                account_id = row['accountId'].strip()
                migration_date = row['migrationDate'].strip()
                
                if account_id and migration_date:
                    accounts.append({
                        'accountId': int(account_id),
                        'migrationDate': migration_date
                    })
        
        print(f"✅ Se leyeron {len(accounts)} cuentas del archivo CSV")
        return accounts
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{csv_file}'")
        return []
    except Exception as e:
        print(f"❌ Error al leer el CSV: {e}")
        return []


def get_account_from_dynamodb(dynamodb, table_name, account_id):
    """
    Consulta una cuenta en DynamoDB por accountId.
    
    Args:
        dynamodb: Cliente de DynamoDB
        table_name (str): Nombre de la tabla
        account_id (str): ID de la cuenta a consultar
        
    Returns:
        dict: Item de DynamoDB o None si no existe
    """
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(
            Key={
                'accountId': account_id
            }
        )
        
        if 'Item' in response:
            return response['Item']
        else:
            return None
            
    except ClientError as e:
        print(f"❌ Error al consultar cuenta {account_id}: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado al consultar cuenta {account_id}: {e}")
        return None


def update_account_migration_date(dynamodb, table_name, account_id, migration_date):
    """
    Actualiza la propiedad migrationDate de una cuenta en DynamoDB.
    
    Args:
        dynamodb: Cliente de DynamoDB
        table_name (str): Nombre de la tabla
        account_id (str): ID de la cuenta a actualizar
        migration_date (str): Fecha de migración
        
    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario
    """
    try:
        table = dynamodb.Table(table_name)
        
        response = table.update_item(
            Key={
                'accountId': account_id
            },
            UpdateExpression='SET migrationDate = :migrationDate',
            ExpressionAttributeValues={
                ':migrationDate': migration_date
            },
            ReturnValues='UPDATED_NEW'
        )
        
        return True
        
    except ClientError as e:
        print(f"❌ Error al actualizar cuenta {account_id}: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado al actualizar cuenta {account_id}: {e}")
        return False


def main():
    """
    Función principal del script.
    """
    print("=" * 80)
    print("ACTUALIZACIÓN DE CUENTAS EN DYNAMODB - MIGRATION DATE")
    print("=" * 80)
    print(f"Tabla: {TABLE_NAME}")
    print(f"Región: {REGION}")
    print(f"Archivo CSV: {CSV_FILE}")
    print("=" * 80)
    print()
    
    # Leer cuentas del CSV
    accounts = read_csv_accounts(CSV_FILE)
    
    if not accounts:
        print("❌ No se encontraron cuentas para procesar")
        return
    
    print()
    
    # Inicializar cliente de DynamoDB
    try:
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        print(f"✅ Conectado a DynamoDB en región {REGION}")
        print()
    except Exception as e:
        print(f"❌ Error al conectar con DynamoDB: {e}")
        return
    
    # Procesar cada cuenta
    success_count = 0
    error_count = 0
    not_found_count = 0
    
    print("Procesando cuentas...")
    print("-" * 80)
    
    for i, account in enumerate(accounts, 1):
        account_id = account['accountId']
        migration_date = account['migrationDate']
        
        print(f"[{i}/{len(accounts)}] Procesando cuenta: {account_id}")
        
        # Verificar que la cuenta existe en DynamoDB
        existing_account = get_account_from_dynamodb(dynamodb, TABLE_NAME, account_id)
        
        if existing_account is None:
            print(f"  ⚠️  Cuenta {account_id} no encontrada en DynamoDB")
            not_found_count += 1
            continue
        
        # Actualizar la cuenta con migrationDate
        if update_account_migration_date(dynamodb, TABLE_NAME, account_id, migration_date):
            print(f"  ✅ Cuenta {account_id} actualizada con migrationDate: {migration_date}")
            success_count += 1
        else:
            print(f"  ❌ Error al actualizar cuenta {account_id}")
            error_count += 1
        
        print()
    
    # Resumen final
    print("=" * 80)
    print("RESUMEN DE ACTUALIZACIÓN")
    print("=" * 80)
    print(f"Total de cuentas procesadas: {len(accounts)}")
    print(f"✅ Actualizaciones exitosas: {success_count}")
    print(f"❌ Errores: {error_count}")
    print(f"⚠️  No encontradas: {not_found_count}")
    print("=" * 80)


if __name__ == "__main__":
    main()
