import netifaces as ni

ni.ifaddresses('eth0')
ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
net = ni.ifaddresses('eth0')[ni.AF_INET][0]['netmask']
print(ip)
print(net)
print(sum([bin(int(x)).count('1') for x in net.split('.')]))
