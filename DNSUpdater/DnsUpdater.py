import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Get the global IP address
response = requests.get('https://api.ipify.org')
global_ip = response.text

# Get the old global IP address
old_global_ip = os.getenv('OLD_GLOBAL_IP')

# If the global IP address has changed, update the DNS record
if global_ip != old_global_ip:
    zoneId = os.getenv('ZONE_ID')
    recordId = os.getenv('RECORD_ID')
    # Set the Cloudflare API URL
    url = f'https://api.cloudflare.com/client/v4/zones/{zoneId}/dns_records/{recordId}'

    # Set the headers
    authEmail = os.getenv('AUTH_EMAIL')
    authKey = os.getenv('AUTH_KEY')
    headers = {
        'X-Auth-Email': authEmail,
        'X-Auth-Key': authKey,
        'Content-Type': 'application/json'
    }

    # Set the data
    recordName = os.getenv('RECORD_NAME')
    data = {
        'type': 'A',
        'name': recordName,
        'content': global_ip,
        'ttl': 120,
        'proxied': True
    }

    # get current date in YYYY-MM-DD HH:MM:SS format
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(current_time, "start to update DNS")

    # Send the PUT request
    response = requests.put(url, headers=headers, json=data)

    # If the request was successful, update the old global IP address
    if response.status_code == 200:
        os.environ['OLD_GLOBAL_IP'] = global_ip
        print("DNS updated")
    else:
        print("DNS update failed", response.text)
    
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(current_time, "finish updating DNS")
