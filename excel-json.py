import pandas as pd
import json

# Lee el archivo Excel (.xlsx)
excel_file = 'concession-data.xlsx'  # Reemplaza con la ruta a tu archivo Excel
df = pd.read_excel(excel_file)

# Convierte el DataFrame a un diccionario
data_dict = df.to_dict(orient='records')

# Convierte el diccionario a una cadena JSON
json_data = json.dumps(data_dict, indent=4)

# Guarda la cadena JSON en un archivo
json_file = 'concession-param.json'  # Reemplaza con la ruta donde quieras guardar el archivo JSON
with open(json_file, 'w') as f:
    f.write(json_data)

print(f"El archivo JSON ha sido guardado en {json_file}")