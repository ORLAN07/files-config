import json
import csv

output_csv_path = "users_normalize.csv"
items = []
# Read the JSON file
with open('backup-users-all.json', 'r') as file:
    data = json.load(file)

# Specify the parameter to extract
param_id = 'id'
param_addresses = 'addresses'
param_addressType = 'addressType'
params_names = ['id', 'addresses']

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
                        'id': param['id']['S'],
                        'city': address['M']['city']['S']
                    })

with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = items[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

    writer.writeheader()
    for item in items:
        writer.writerow(item)