#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gw2api, sys
from gw2api import format_gold as gold

def main():
	transactions_path='commerce/transactions/current/sells'
	query = gw2api.get_multi(['account', transactions_path])
	if len(query[transactions_path]) == 0:
		if not args.quiet:
			print(_('No current sell transactions of %s.') % query['account']['name'])
		sys.exit(1)
	if not args.quiet:
		print(_('Current sell transactions of %s:') % query['account']['name'])
		items = {}
		for item in gw2api.get_list('items',
		 map(lambda transaction: transaction['item_id'], query[transactions_path])):
			items[item['id']] = item
		for transaction in sorted(query[transactions_path],
		 key=lambda transaction: transaction['created']):
			print('%3d %s - %s' % ( transaction['quantity'], 
			 items[transaction['item_id']]['name'], gold(transaction['price'])))

# PSEUDO-I18N
messages = ({'de': {}})

messages['de']['Current sell transactions of %s:'] = \
 u'Aktuelle Verkaufstransaktionen von %s:'
messages['de']['No current sell transactions of %s.'] = \
 u'Keine aktuellen Verkaufstransaktionen von %s.'

def _(text):
	if config['language'] in messages:
		if text in messages[config['language']]:
			return messages[config['language']][text]
	return text

# MAIN
import argparse
argparser=argparse.ArgumentParser(description='List all unfullfilled sell transactions.')
argparser.add_argument('profile', default='default', nargs='?', metavar='PROFILE',
 help='Profile in INI file')
argparser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
 help='Dont''t output any text.')
args = argparser.parse_args()

config = gw2api.init(args.profile)

main()
