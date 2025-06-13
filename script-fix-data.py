import json

# Function to update the second JSON based on the first JSON
def update_agreements(data1, data2):
    # Create a mapping from stateid to the corresponding agreement details
    agreement_map = {item['stateid']: item for item in data1['items']}
    
    # Iterate through the items in the second JSON
    for item in data2['items']:
        # Check if stationId matches any stateid from the first JSON
        if item['stationId'] in agreement_map:
            # Update the fields in the second JSON
            print(f">>>{item['stationId']}>>>{agreement_map[item['stationId']]['agreementid']}")
            item['concessionAgreementId'] = agreement_map[item['stationId']]['agreementid']
            item['collectionAgreement'] = agreement_map[item['stationId']]['collectionAgreement']
            item['operatorCode'] = agreement_map[item['stationId']]['Cod. Operador']
    
    return data2

# Function to read a JSON file
def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to write a JSON file
def write_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# File paths for input and output JSON files
file1_path = 'file-input-config.json'  # First JSON file
file2_path = 'salida.json'  # Second JSON file
output_file_path = 'updated_file2.json'  # Output JSON file

# Read the JSON files
data1 = read_json(file1_path)
data2 = read_json(file2_path)

# Update the second JSON based on the first JSON
updated_data2 = update_agreements(data1, data2)

# Write the updated data to a new JSON file
write_json(output_file_path, updated_data2)

print(f"The second JSON file has been updated and saved as '{output_file_path}'.")