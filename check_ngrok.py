import subprocess
import requests
import time
import logging

logging.basicConfig(filename='check_ngrok.log', level=logging.WARNING)

def get_ngrok_url():
	try:
		r = requests.get('http://localhost:4040/api/tunnels')
		r_json = r.json()
		url = r_json['tunnels'][0]['public_url']
		return url
	except:
		logging.warning("getting url encountered exception, retrying in 5 secondss\n")
		time.sleep(5)
                get_ngrok_url(logfile)

#with open('ngrok.out.txt', 'w') as f:
#	subprocess.call(['/home/pi/ngrok', 'tcp', '22'], stdout=f)

url = get_ngrok_url()
logging.warning(url)

result = requests.post(
            "https://api.mailgun.net/v3/imageous.io/messages",
            auth=("api", "key-9f9feb3fc05b6bf638c39ce54f974ec2"),
            data={"from": "Roby <roby@imageous.io>",
                    "to": ['justin@imageous-inc.com', 'justin@imageous-inc.com'],
                    "subject": "New ngrok connection for raspi",
                    "text": url})
result = requests.post(
            "https://api.mailgun.net/v3/imageous.io/messages",
            auth=("api", "key-9f9feb3fc05b6bf638c39ce54f974ec2"),
            data={"from": "Roby <roby@imageous.io>",
                    "to": ['ben@imageous-inc.com', 'ben@imageous-inc.com'],
                    "subject": "New ngrok connection for raspi",
                    "text": url})

while(1):
    time.sleep(10000)
