import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Get the global IP address
response = requests.get('https://api.ipify.org')
global_ip = response.text

# Get the old global IP address by reading file ipaddress.txt
file_path = os.environ.get('IP_ADDRESS_FILE')
old_global_ip = ''
with open(file_path, 'r') as file:
    old_global_ip = file.read().strip()

# get current date in YYYY-MM-DD HH:MM:SS format
now = datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

# If the global IP address has changed, update the DNS record
if global_ip == old_global_ip:
    print(current_time, "Global IP address has not changed")
else:
    zoneId = os.getenv('ZONE_ID')
    # Set the Cloudflare API URL
    url_template = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'

    # Set the headers
    authEmail = os.getenv('AUTH_EMAIL')
    authKey = os.getenv('AUTH_KEY')
    headers = {
        'X-Auth-Email': authEmail,
        'X-Auth-Key': authKey,
        'Content-Type': 'application/json'
    }

    # get all record names
    records_str = os.getenv('RECORDS')
    # part record to JSON
    records = json.loads(records_str)

    for record in records:
        record_type = record.get('type')
        recordId = record.get('id')
        recordName = record.get('name').strip()
        proxied = record.get('proxied')
        url = url_template.format(zoneId, recordId)  # Format the URL with zoneId and recordId

        data = {
            'type': record_type,
            'name': recordName,
            'content': global_ip,
            'ttl': 120,
            'proxied': proxied
        }

        print(current_time, "start to update DNS", recordName, global_ip)

        # Send the PUT request
        response = requests.put(url, headers=headers, json=data)

        # If the request was successful, update the old global IP address
        if response.status_code == 200:
            with open(file_path, 'w') as file:
                file.write(global_ip)
            print("DNS updated")
        else:
            print("DNS update failed", response.text)
        
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time, "finish updating DNS", recordName, global_ip)
