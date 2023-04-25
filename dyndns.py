#!/usr/bin/env python3

from domeneshop import Client
import configparser
import requests
import sys
import logging
import os

homefolder = os.path.expanduser('~')
logpath = os.path.join(homefolder, '.dyndns-domeneshop')

if not os.path.isdir(logpath):
	os.mkdir(logpath)

logging.basicConfig(
	filename=os.path.join(logpath, 'info.log'),
	level=logging.INFO,
	format="%(asctime)s:%(levelname)s:%(message)s"
	)

work_dir = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(work_dir, 'settings.ini'))

token = config.get('secrets', 'token')
secret = config.get('secrets', 'secret')
domain = config.get('config', 'domain')
record = config.get('config', 'record')
ttl = int(config.get('config', 'ttl'))

ip_service = 'http://ifconfig.me'
ip6_service = 'https://ipv6.icanhazip.com'
user_agent = {'User-Agent': 'curl'}

def log(msg):
	print(msg)
	logging.info(msg)

if __name__ == "__main__":
	client = Client(token, secret)
	domains = client.get_domains()
	for d in domains:
		if d['domain'] == domain:
			domain_id = d['id']
			break

	if not domain_id:
		log("Domain {} not found".format(domain))
		sys.exit(1)

	records = client.get_records(domain_id)
	for r in records:
		print(r)
		if r['host'] == record and r['type'] == 'A':
			record_id = r['id']
#			break
		if r['host'] == record and r['type'] == 'AAAA':
			record6_id = r['id']
#			break
	print(record_id)
	print(record6_id)
	if not record_id or not record6_id:
		log("Record {} of type A/AAAA not found".format(record))
		sys.exit(1)
	
	record_data = client.get_record(domain_id, record_id)
	record6_data = client.get_record(domain_id, record6_id)
	current_ip = requests.get(ip_service, headers=user_agent).text.strip()
	current_ipv6 = requests.get(ip6_service, headers=user_agent).text.strip()

	if record_data['data'] == current_ip:
		log("DNS is up to date with current IPv4 address ({})".format(current_ip))
		log("Nothing to do. Bye bye!")
	else:
		log("DNS has {}, but current IPv4 is {}".format(record_data['data'], current_ip))
		new_record = {
			'data': current_ip,
			'host': record,
			'ttl': ttl,
			'type': 'A'
		}
		log("Will send this as new record data: {}".format(new_record))
		try:
			log("Sending new record data to Domeneshop...")
			client.modify_record(domain_id, record_id, new_record)
			r = client.get_record(domain_id, record_id)['data']
			log("Great success! DNS now has {} for {}.{}".format(r, record, domain))
		except:
			log("Something went wrong. Either you or Domeneshop fucked up....")

	if record6_data['data'] == current_ipv6:
		log("DNS is up to date with current IPv6 address ({})".format(current_ipv6))
		log("Nothing to do. Bye bye!")
	else:
		log("DNS has {}, but current IPv6 is {}".format(record6_data['data'], current_ipv6))
		new_record = {
			'data': current_ipv6,
			'host': record,
			'ttl': ttl,
			'type': 'AAAA'
		}
		log("Will send this as new record data: {}".format(new_record))
		try:
			log("Sending new record data to Domeneshop...")
			client.modify_record(domain_id, record6_id, new_record)
			r = client.get_record(domain_id, record6_id)['data']
			log("Great success! DNS now has {} for {}.{}".format(r, record, domain))
		except:
			log("Something went wrong. Either you or Domeneshop fucked up....")
			log(sys.exc_info()[1])
