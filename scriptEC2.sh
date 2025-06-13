#!/bin/bash

# Use this for your user data (script from top to bottom)

# install httpd (Linux 2 version)

yum update -y

yum install -y httpd

systemctl start httpd

systemctl enable httpd

echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html


ssh -i "key_name.pem" user@ip





aws lambda list-event-source-mappings --function-name fap-commons-pro-a5-process-toll-transaction --region us-east-2
aws lambda update-event-source-mapping --uuid 92f71306-6ac6-44a7-b76b-8e8bf13e2129 --no-enabled --region us-east-2
aws lambda update-event-source-mapping --uuid 92f71306-6ac6-44a7-b76b-8e8bf13e2129 --enabled --region us-east-2
