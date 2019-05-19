#!/usr/bin/env python3

from domeneshop import Client
import configparser
import requests
import sys

config = configparser.ConfigParser()
config.read('settings.ini')

token = config.get('secrets', 'token')
secret = config.get('secrets', 'secret')
domain = config.get('config', 'domain')
record = config.get('config', 'record')

ip_service = 'http://ip.xt.gg'
user_agent = {'User-Agent': 'curl'}

if __name__ == "__main__":
	client = Client(token, secret)
	domains = client.get_domains()
	for d in domains:
		if d['domain'] == domain:
			domain_id = d['id']
			break

	if not domain_id:
		print("Domain {} not found".format(domain))
		sys.exit(1)

	records = client.get_records(domain_id)
	for r in records:
		if r['host'] == record and r['type'] == 'A':
			record_id = r['id']
			break

	if not record_id:
		print("Record {} not found".format(record))
		sys.exit(1)
	
	record_data = client.get_record(domain_id, record_id)
	current_ip = requests.get(ip_service, headers=user_agent).text.strip()

	if record_data['data'] == current_ip:
		print("DNS is up to date with current IPv4 address ({})".format(current_ip))
		print("Nothing to do. Bye bye!")
	else:
		print ("DNS has {}, but current IPv4 is {}".format(record_data['data'], current_ip))
		new_record = {
			'data': current_ip,
			'host': record,
			'ttl': 3600,
			'type': 'A'
		}
		print("Will send this as new record data: {}".format(new_record))
		try:
			print("Sending new record data to Domeneshop...")
			client.modify_record(domain_id, record_id, new_record)
			r = client.get_record(domain_id, record_id)['data']
			print("Great success! DNS now has {} for {}.{}".format(r, record, domain))
		except:
			print("Something went wrong. Either you or Domeneshop fucked up....")

