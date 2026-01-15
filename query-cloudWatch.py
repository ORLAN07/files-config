#!/usr/bin/env python3
"""
Script para exportar logs de CloudWatch a CSV
Extrae: @requestId, codigo, destinatario
Usa paginación automática de CloudWatch para obtener todos los registros
"""

import boto3
import csv
import re
from datetime import datetime
import sys

# Configuración
LOG_GROUP = '/aws/lambda/fap-toll-pro-notifications-center'
REGION = 'us-east-2'

# Rango de fechas
START_DATE = datetime(2025, 12, 1, 0, 0, 0)
END_DATE = datetime(2025, 12, 31, 23, 59, 59)

# Nombre del archivo de salida
OUTPUT_FILE = 'cloudwatch_export.csv'

def extract_request_id(message):
    """Extrae el requestId del mensaje"""
    match = re.search(r'\s([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\s+INFO', message)
    return match.group(1) if match else ''

def extract_codigo(message):
    """Extrae el código de notificación del mensaje"""
    match = re.search(r'"msg":"Inicia.*?\[(\d+)\]', message)
    return match.group(1) if match else ''

def extract_destinatario(message):
    """Extrae el destinatario (email o teléfono) del mensaje"""
    match = re.search(r'"msg":\{"to":\[([^\]]+)\]', message)
    if match:
        # Limpiar comillas extras
        dest = match.group(1)
        dest = dest.replace('"""', '').replace('"', '').strip()
        return dest
    return ''

def main():
    print(f"🚀 Iniciando exportación de logs de CloudWatch")
    print(f"📁 Log Group: {LOG_GROUP}")
    print(f"🌍 Región: {REGION}")
    print(f"📅 Período: {START_DATE} a {END_DATE}")
    print(f"💾 Archivo de salida: {OUTPUT_FILE}")
    print("="*80)
    
    # Convertir a timestamps en milisegundos
    start_time = int(START_DATE.timestamp() * 1000)
    end_time = int(END_DATE.timestamp() * 1000)
    
    # Crear cliente de CloudWatch Logs
    client = boto3.client('logs', region_name=REGION)
    
    # Abrir archivo CSV para escritura
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['@requestId', 'codigo', 'destinatario'])
        
        next_token = None
        total_events = 0
        total_written = 0
        page_num = 0
        
        try:
            while True:
                page_num += 1
                
                # Preparar parámetros
                params = {
                    'logGroupName': LOG_GROUP,
                    'startTime': start_time,
                    'endTime': end_time
                }
                
                if next_token:
                    params['nextToken'] = next_token
                
                # Llamar a filter_log_events
                print(f"📄 Página {page_num} - Obteniendo eventos...", end='')
                try:
                    response = client.filter_log_events(**params)
                except Exception as e:
                    print(f"\n❌ Error en la llamada API: {str(e)}")
                    break
                
                events = response.get('events', [])
                
                if not events:
                    print(f"\nℹ️  No hay más eventos")
                    break
                
                # Procesar eventos
                page_events = 0
                page_written = 0
                
                for event in events:
                    message = event['message']
                    total_events += 1
                    page_events += 1
                    
                    # Extraer campos
                    request_id = extract_request_id(message)
                    codigo = extract_codigo(message)
                    destinatario = extract_destinatario(message)
                    
                    # Solo escribir si tiene código o destinatario
                    if codigo or destinatario:
                        writer.writerow([request_id, codigo, destinatario])
                        total_written += 1
                        page_written += 1
                
                print(f" ✓ {page_events:,} eventos ({page_written:,} exportados)")
                print(f"   📊 Total acumulado: {total_events:,} procesados | {total_written:,} exportados")
                
                # Guardar en disco cada página
                csvfile.flush()
                
                # Verificar si hay más páginas
                if 'nextToken' in response:
                    next_token = response['nextToken']
                else:
                    print(f"\n✅ Todas las páginas procesadas")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n⚠️  Exportación interrumpida por el usuario")
            print(f"📊 Eventos procesados: {total_events:,}")
            print(f"📝 Registros escritos: {total_written:,}")
            print(f"📄 Páginas procesadas: {page_num}")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Error durante la exportación: {str(e)}")
            print(f"📊 Eventos procesados: {total_events:,}")
            print(f"📝 Registros escritos: {total_written:,}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    print("\n" + "="*80)
    print("✅ EXPORTACIÓN COMPLETADA EXITOSAMENTE!")
    print("="*80)
    print(f"📁 Archivo: {OUTPUT_FILE}")
    print(f"📊 Total eventos procesados: {total_events:,}")
    print(f"📝 Total registros exportados: {total_written:,}")
    print(f"📄 Total páginas procesadas: {page_num}")

if __name__ == '__main__':
    main()
