#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, json, pycurl
try:
	from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO
try:
	from configparser import ConfigParser
except ImportError:
	from ConfigParser import ConfigParser

# These scripts expect an ini-file, either config.ini at the script location or ~/.gw2rc
# 
# [default]
# api_key=<YOUR API KEY>
# language=<LANG>  # default: en
#
# Every profile is an own section, [default] being the default one
# Configuration items are returned by init to make i18n and application-specific options possible

def init(profile = 'default', schema='latest'):
	global gw2_config
	config_parser = ConfigParser();
	config_parser.read([
	 os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'),
	 os.path.expanduser('~/.gw2rc')])
	gw2_config = {}
	gw2_config['schema'] = schema
	gw2_config['api_key'] = config_parser.get(profile, 'api_key')
	gw2_config['language'] = config_parser.get(profile,
	 'language') if config_parser.has_option(profile, 'language') else 'en'

	gw2_config.update({'copper_unit': 'c', 'silver_unit': 's','gold_unit': 'g'});
	if gw2_config['language'].startswith('de'):
		gw2_config.update({'copper_unit': 'k', 'silver_unit': 's','gold_unit': 'g'});
	if gw2_config['language'].startswith('es'):
		gw2_config.update({'copper_unit': 'b', 'silver_unit': 'p','gold_unit': 'o'});
	if gw2_config['language'].startswith('fr'):
		gw2_config.update({'copper_unit': 'c', 'silver_unit': 'a','gold_unit': 'o'});

	config_items = {}
	for key, value in config_parser.items(profile):
		config_items[key] = value
	config_items['language'] = gw2_config['language']
	return config_items


def create_handle(path):
	if not 'gw2_config' in globals():
		init()
	handle = pycurl.Curl()
	handle.setopt(pycurl.URL, 'https://api.guildwars2.com/v2/%s' % path)
	handle.setopt(pycurl.HTTPHEADER, [
	 'Accept: application/json',
	 'X-Schema-Version: %s' % gw2_config['schema'],
	 'Authorization: Bearer %s' % gw2_config['api_key'],
	 'Accept-Language: %s' % gw2_config['language']])
	handle.setopt(pycurl.FOLLOWLOCATION, True)
	return handle


def get_single(path):
	if not 'gw2_config' in globals():
		init()
	handle = create_handle(path)
	response = BytesIO()
	handle.setopt(pycurl.WRITEFUNCTION, response.write)
	handle.perform()
	status = handle.getinfo(pycurl.HTTP_CODE)
	if not status in [200, 204, 206]:
		text = response.getvalue()
		raise IOError('%s\nError %s [%s]' % (text, status, path))
	handle.close()
	return json.loads(response.getvalue())


def get_multi(paths):
	if not 'gw2_config' in globals():
		init()
	requests = []
	multi = pycurl.CurlMulti()
	for path in paths:
		handle = create_handle(path)
		response = BytesIO()
		request = ({'path': path, 'response': response, 'handle': handle})
		handle.setopt(pycurl.WRITEFUNCTION, request['response'].write)
		multi.add_handle(request['handle'])
		requests.append(request)
	num_handles = len(requests)
	while num_handles:
		ret = multi.select(1.0)
		if ret == -1:
			continue
		while 1:
			ret, num_handles = multi.perform()
			if ret != pycurl.E_CALL_MULTI_PERFORM:
				break
	results = {}
	for request in requests:
		status = request['handle'].getinfo(pycurl.HTTP_CODE)
		if not status in [200, 204, 206]:
			text = request['response'].getvalue()
			raise IOError('%s\nError %s [%s]' % (text, status, request['path']))
		request['handle'].close()
		results[request['path']] = json.loads(request['response'].getvalue())
	return results


def get_list(path, ids, id_field='ids', chunk_size=50):
	if ids == 'all':
		return get_single('%s?%s=all' % (path, id_field))
	chunks = []
	chunk = []
	for id in set(ids):
		if id == None:
			continue
		chunk.append(id)
		if len(chunk)>=chunk_size:
			chunks.append(chunk)
			chunk=[]
	chunks.append(chunk)
	paths = []
	for chunk in chunks:
		if chunk == None or not chunk:
			continue
		paths.append('%s?%s=%s' % (path, id_field, ','.join(map(str,chunk))))
	responses = get_multi(paths)
	items = []
	for response in responses:
		items.extend(responses[response])
	return items


def format_gold(copper):
	if not 'gw2_config' in globals():
		init()
	groups = re.match('^(\\d*?)(\\d{0,2}?)(\\d{0,2})$', str(copper)).groups()
	parts = []
	if groups[0]:
		parts.append('%s%s' % (groups[0], gw2_config['gold_unit']))
	if groups[1]:
		parts.append('%s%s' % (groups[1], gw2_config['silver_unit']))
	if groups[2]:
		parts.append('%s%s' % (groups[2], gw2_config['copper_unit']))
	else:
		parts.append('0%s' % gw2_config['copper_unit'])
	return ' '.join(parts)


if __name__ == '__main__':
	import argparse

	argparser=argparse.ArgumentParser(description='Get raw json from GW2 API v2')
	argparser.add_argument(dest='url', metavar='URL', help='URL',
	 nargs='?', default='../v2.json')
	argparser.add_argument('-p', '--profile', dest='profile', default='default',
	 help='Profile in INI file')
	argparser.add_argument('-s', '--schema', dest='schema', default='latest',
	 help='Schema version (UTC ISO8601 timestamp)')
	args = argparser.parse_args()

	config = init(args.profile, args.schema)
	print(json.dumps(get_single(args.url), indent=4));
