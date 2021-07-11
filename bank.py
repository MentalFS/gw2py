#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gw2api
from gw2api import format_gold as gold

def main():
	account = gw2api.get_multi(['account', 'account/bank'])
	print((_("Bank contents of %s:") % account['account']['name']))
	item_ids = set([item['id'] if item else None for item in account['account/bank']])
	
	item_info = {}
	for item in gw2api.get_list('items', item_ids):
		item_info[item['id']] = item
	
	for slot in account['account/bank']:
		if slot == None:
			print(('    '+_('<empty>')))
			continue
		item_name = item_info[slot['id']]['name'] if slot['id'] in item_info \
		 else _('<unknown ID: %d>') % slot['id']
		print(("%3s %s" % (slot['count'], item_name)))

	

# PSEUDO-I18N
messages = ({'de': {
	'Bank contents of %s:': u'Bankinhalt von %s:',
	'<empty>': u'<leer>',
	'<unknown ID: %d>': u'<unbekannte ID: %d>'
}})
def _(text):
	if config['language'] in messages:
		if text in messages[config['language']]:
			return messages[config['language']][text]
	return text

# MAIN
import argparse
argparser=argparse.ArgumentParser(description='List the items of an account\'s bank tab.')
argparser.add_argument('profile', default='default', nargs='?', metavar='PROFILE',
 help='Profile in INI file')
args = argparser.parse_args()

config = gw2api.init(args.profile)

main()
