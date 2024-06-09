import json
import csv

output_csv_path = "corporate_normalize.csv"
items = []
# Read the JSON file
with open('backup-corporate-all.json', 'r') as file:
    data = json.load(file)

# Specify the parameter to extract
param_addressType = 'addressType'
params_names = ['corporateNumber', 'addresses']

# Extract the specified parameter from each object in the array
params = [{param_name: obj.get(param_name) for param_name in params_names} for obj in data]

# Print the extracted parameters

for param in params:
    if param['addresses']:
        print(param['addresses'])
        for address in param['addresses']['L']:
            if param_addressType in address['M']:
                if address['M']['addressType']['S'] == 'Principal':
                    items.append({
                        'corporateNumber': param['corporateNumber']['S'],
                        'city': address['M']['city']['S']
                    })

with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = items[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

    writer.writeheader()
    for item in items:
        writer.writerow(item)