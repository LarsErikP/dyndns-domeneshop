#!/usr/bin/env python3

import configparser
import requests
import logging
import os

homefolder = os.path.expanduser('~')
logpath = os.path.join(homefolder, '.dyndns-domeneshop')

if not os.path.isdir(logpath):
	os.mkdir(logpath)

logging.basicConfig(
	filename=os.path.join(logpath, 'simple_client_info.log'),
	level=logging.INFO,
	format="%(asctime)s:%(levelname)s:%(message)s"
	)

work_dir = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(work_dir, 'settings.ini'))

token = config.get('secrets', 'token')
secret = config.get('secrets', 'secret')
domain = config.get('config', 'domain')


ip_service = 'http://ifconfig.me'
ip6_service = 'https://ipv6.icanhazip.com'
user_agent = {'User-Agent': 'curl'}

def log(msg):
	print(msg)
	logging.info(msg)

if __name__ == "__main__":
    ipv4 = requests.get(ip_service, headers=user_agent).text.strip()
    ipv6 = requests.get(ip6_service, headers=user_agent).text.strip()
    addresses = [ ipv4, ipv6 ]

    for ip in addresses:
        url = f"https://{token}:{secret}@api.domeneshop.no/v0/dyndns/update?hostname={domain}&myip={ip}"
        r = requests.get(url)
        if r.status_code == 204:
            log("Great success! DNS now have {} for {}".format(ip, domain))
        elif r.status_code == 404:
            log("ERROR: You don't own that domain: {}".format(domain))
        else:
            log("ERROR: The request failed with return code {}".format(r))

