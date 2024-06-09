import boto3
import csv

#script users
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

table = dynamodb.Table('fap-corporate-info')

csv_file_path = "fap_corporate_pro.csv"
output_csv_path = "corporate_updated_addresses.csv"
updated_items = []
item_field = "Item"
addresses_field = "addresses"

with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
    # Use DictReader with the specified delimiter and skip the first row (headers)
    reader = csv.DictReader(csvfile, delimiter=';', skipinitialspace=True)

    for row in reader:
        id=row['corporateNumber']

        # query by id
        responseGet = table.get_item(Key={
            'corporateNumber': id
        })

        if item_field in responseGet:
            item = responseGet['Item']
            #set city name correct
            if addresses_field in item:
                addresses = item['addresses']
                for address in addresses:
                    if address['addressType'] == "Principal":
                        address['city'] = row['cityNew']
                        break
                #update address city
                update_expression='SET addresses = :new_addresses'
                expression_values={':new_addresses': addresses}

                responseUpdate = table.update_item(
                    Key={'corporateNumber': id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_values,
                    ReturnValues='UPDATED_NEW'
                )
                updated_items.append({
                    'corporateNumber': id,
                    'addresses': responseUpdate['Attributes']
                })

with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    if len(updated_items) > 0:
        fieldnames = updated_items[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

        writer.writeheader()
        for item in updated_items:
            writer.writerow(item)

print(f"Updated items saved to {output_csv_path}")