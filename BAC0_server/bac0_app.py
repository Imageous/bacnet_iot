import BAC0
import time
from flask import Flask, request, jsonify
import logging
import sys
import netifaces as ni


logging.basicConfig(filename='log_bac0_app.log', level=logging.WARNING)

STATIC_BACNET_IP = '192.168.1.104/24'


# fetches the subnet mask for the specified interface (ex. eth0, eth1) and converts to CIDR code
def get_subnet_mask(interface):
	netmask = ni.ifaddresses(interface)[ni.AF_INET][0]['netmask']
	return sum(bin(int(x)).count('1') for x in netmask.split('.'))

# Look for IP assigned to eth0 interface, assumes device is connected to BACnet network on eth0
logging.warning("Attempting to discover IP address on eth0 interface...")
try:
	ni.ifaddresses('eth0')
	eth1_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
	eth1_ip = eth1_ip + '/' + str(get_subnet_mask('eth0'))
	print(eth1_ip)
	bacnet = BAC0.connect(ip=eth1_ip)
	logging.warning("Discovered %s on eth0 for BACnet IP" % eth1_ip)
	print("Discovered %s on eth1 for BACnet IP, connected" % eth1_ip)
except:
	logging.warning("Available interfaces: %s" % ni.interfaces())
	logging.warning("Exception occured: %s \n Failed to read IP address on eth0, defaulting to static IP setting: %s" % (str(sys.exc_info()), STATIC_BACNET_IP))
	print("Establishing BACnet connection on: %s" % STATIC_BACNET_IP)
	bacnet = BAC0.connect(ip=STATIC_BACNET_IP)
#bacnet.whois()
#time.sleep(2)
#print(bacnet.devices)

#request_object_list = [('analogValue', 90)]
#device = BAC0.device('1201:14', 332, bacnet, object_list=request_object_list, segmentation_supported=False)
#time.sleep(2)
#print(device.points)
#print(device['analogValue'])

# cache a mapping of device_id to addresses for faster lookup
devices = bacnet.whois()
#print(bacnet.devices)
time.sleep(2)
device_mapping = {}
for device in devices:
	if isinstance(device, tuple):
		device_mapping[device[1]] = device[0]
		logging.info("Detected device %s with address %s" % (str(device[1]), str(device[0])))
#print(device_mapping)

app = Flask(__name__)

# function to look up the address for the specified device_id (int)
def get_address(device_id):
	target_address = None
	try:
		devices = bacnet.whois()
		time.sleep(2)
		for device in devices:
			if isinstance(device, tuple):
				if device[1] == int(device_id):
					target_address = device[0]
					logging.warning("Target device found with address: %s" % target_address)
	except:
		logging.warning("Searching for target device on network excountered exception")
		raise
	return target_address

def get_cached_address(device_id):
	target_address = device_mapping[int(device_id)]
	if target_address is None:
		logging.warning("Failed to find a device mapping for device id: %s" % str(device_id))
	return target_address

# create endpoints
def create_server(app):
	
	@app.route('/read', methods=['POST'])
	def do_read():

		try:
			device_id = request.form['device_id']
			object_id = request.form['object_id']
			object_type = request.form['object_type']
		except:
			err_msg = "Read request was missing a required parameter. Required: [device_id, object_id, object_type]"
			logging.warning(err_msg + " Exception: " + str(sys.exc_info()))
			return jsonify({"status_code": 500, "description": err_msg})

		# get address of target device
		try:
			#target_address = get_address(int(device_id))
			target_address = get_cached_address(int(device_id))
		except:
			logging.warning("Exception: " + str(sys.exc_info()))
			return jsonify({"status_code": 500, "description": "Searching for device on network encountered exception"})
		if target_address is None:
			err_msg = "Address was not found for device %s" % device_id
			logging.warning(err_msg)
			return jsonify({"status_code": 500, "description": err_msg})
			#raise Exception("Address was not found for device %s", device_id)
		# create BACpypes read statement and run
		bp_stmt = '%s %s %s presentValue' % (target_address, object_type, object_id)
		logging.warning("Excecuting BACpypes statement: %s", bp_stmt)
		try:
			result = bacnet.read(bp_stmt)
			nonflt = ["0", "1", "active", "inactive"]
			if result not in nonflt:
				try:
					rounded = round(float(result), 1)
				except:
					logging.warning("Failed to convert "+result+" to float for rounding.")
				result = rounded
		except:
			logging.warning("BACnet read failed. Exception: " + str(sys.exc_info()))
			return jsonify({"status_code": 500, "description": "BACnet read failed"})
		return jsonify({"status_code": 200, "value": result})


	@app.route('/write', methods=['POST'])
	def do_write():
		try:
			device_id = request.form['device_id']
			object_id = request.form['object_id']
			object_type = request.form['object_type']
			value = request.form['value']
		except:
			err_msg = "Write request was missing a required parameter. Required: [device_id, object_id, object_type, value]"
			logging.warning(err_msg)
			return jsonify({"status_code": 500, "description": err_msg})

		# get address of target device 
		try:
			target_address = get_address(int(device_id))
		except:
			logging.warning("Exception: " + str(sys.exc_info()))
			return jsonify({"status_code": 500, "description": "Searching for device on network encountered exception"})
		if target_address is None:
			err_msg = "Address was not found for device %s" % device_id
			logging.warning(err_msg)
			return jsonify({"status_code": 500, "description": err_msg})
			#raise Exception("Address was not found for device %s", device_id)

		# create BACpypes write statement and run
		bp_stmt = '%s %s %s presentValue %s' % (target_address, object_type, object_id, value)
		logging.warning("Excecuting BACpypes statement: %s", bp_stmt)
		try:
			result = bacnet.write(bp_stmt)
		except:
			logging.warning("BACnet write failed. Exception: " + str(sys.exc_info()))
			return jsonify({"status_code": 500, "description": "BACnet write failed"})
		return jsonify({"status_code": 200})

	return app

print("Creating server...")
app = create_server(app)

if __name__ == '__main__':
	print("Running BAC0 API server")
	app.run(port=5678)
