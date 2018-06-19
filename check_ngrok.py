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

def get_serial():
    #Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR00000000000"

    return cpuserial

#with open('ngrok.out.txt', 'w') as f:
#	subprocess.call(['/home/pi/ngrok', 'tcp', '22'], stdout=f)

url = get_ngrok_url()
logging.warning(url)

result = requests.post(
            "https://api.mailgun.net/v3/imageous.io/messages",
            auth=("api", "key-f7371ec0910d2c9b2e99e83a1f496e44"),
            data={"from": "Roby <roby@imageous.io>",
                    "to": ['justin@imageous-inc.com', 'justin@imageous-inc.com'],
                    "subject": "New ngrok connection for raspi",
                    "text": url + '\nDevice: ' + get_serial()})

#result = requests.post(
#            "https://api.mailgun.net/v3/imageous.io/messages",
#            auth=("api", "key-f7371ec0910d2c9b2e99e83a1f496e44"),
#            data={"from": "Roby <roby@imageous.io>",
#                    "to": ['ben@imageous-inc.com', 'ben@imageous-inc.com'],
#                    "subject": "New ngrok connection for raspi",
#                    "text": url + '\nDevice: ' + get_serial()})

while(1):
    time.sleep(10000)
