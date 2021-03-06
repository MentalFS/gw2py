#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gw2api, sys
from gw2api import format_gold as gold

def main():
	transactions_path='commerce/transactions/current/buys'
	query = gw2api.get_multi(['account', transactions_path])
	if len(query[transactions_path]) == 0:
		if not args.quiet:
			print((_('No current buy transactions of %s.') % query['account']['name']))
		sys.exit(1)
	if not args.quiet:
		print((_('Current buy transactions of %s:') % query['account']['name']))
		items = {}
		for item in gw2api.get_list('items',
		 [transaction['item_id'] for transaction in query[transactions_path]]):
			items[item['id']] = item
		for transaction in sorted(query[transactions_path],
		 key=lambda transaction: transaction['created']):
			print(('%3d %s - %s' % ( transaction['quantity'],
			 items[transaction['item_id']]['name'], gold(transaction['price']))))

# PSEUDO-I18N
messages = ({'de': {
	'Current buy transactions of %s:': u'Aktuelle Einkaufstransaktionen von %s:',
	'No current buy transactions of %s.': u'Keine aktuellen Einkaufstransaktionen von %s.'
}})
def _(text):
	if config['language'] in messages:
		if text in messages[config['language']]:
			return messages[config['language']][text]
	return text

# MAIN
import argparse
argparser=argparse.ArgumentParser(description='List all unfullfilled buy transactions.')
argparser.add_argument('profile', default='default', nargs='?', metavar='PROFILE',
 help='Profile in INI file')
argparser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
 help='Dont''t output any text.')
args = argparser.parse_args()

config = gw2api.init(args.profile)

main()
