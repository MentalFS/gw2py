#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gw2api
from gw2api import format_gold as gold

def main():
	ignored_items = [ 19983 ]
	
	characters_path='characters?page=0'
	query = gw2api.get_multi(['account', 'account/bank', 'account/materials', characters_path])
	material_ids = map(lambda material: material['id'], query['account/materials'])
	item_ids = set(map(lambda item: item['id'] if item else None,
	 query['account/bank'] + query['account/materials']))
	
	if not args.short:
		print(_('Analyzing storage of %s...') % query['account']['name'])
		print('')
	
	inventory_slots = []
	for character in query[characters_path]:
		for bag in character['bags']:
			if bag == None:
				continue
			for slot in bag['inventory']:
				if slot == None:
					continue
				if slot['id'] in material_ids:
					inventory_slots.append(slot)
	item_counts = {}
	for item in query['account/bank'] + query['account/materials'] + inventory_slots:
		if item == None:
			continue
		if item['id'] not in item_counts:
			item_counts[item['id']] = 0
		if item['id'] in ignored_items:
			continue
		item_counts[item['id']] += item['count']
	
	item_info = {}
	if args.verbose: 
		for item in gw2api.get_list('items', item_ids):
			item_info[item['id']] = item
	
	item_prices = {}
	for item in gw2api.get_list('commerce/prices', item_ids):
		item_prices[item['id']] = item
	
	material_names = {}
	item_material = {}
	if not args.short:
		for material in gw2api.get_list('materials', 'all'):
			material_id = material['id']
			material_names[material_id] = material['name']
			for item in material['items']:
				item_material[item] = material_id
	
	
	total_sum_buy = 0
	total_sum_sell = 0
	largest_stack = ({'item': -1, 'sum_buy': 0, 'sum_sell': 0})
	largest_single = ({'item': -1, 'sum_buy': 0, 'sum_sell': 0})
	material_sums = {}
	nonmaterial_sum_buy = 0
	nonmaterial_sum_sell = 0
	for item in item_ids:
		if item == None:
			continue
		if item not in item_prices:
			continue
		
		count = item_counts[item]
		if count == 0:
			continue
		
		sum_buy = item_prices[item]['buys']['unit_price'] * count
		sum_sell = item_prices[item]['sells']['unit_price'] * count
	
		if args.verbose:
			print(_('Adding %s - %d items, %s / %s') %
			 (item_info[item]['name'] if item in item_info else '[%d]' % item,
			 count, gold(sum_buy), gold(sum_sell)))
		largest = largest_single if count == 1 and not item in material_ids else largest_stack
		if sum_buy > largest['sum_buy']:
			largest['item'] = item
			largest['sum_buy'] = sum_buy
			largest['sum_sell'] = sum_sell
		if item in item_material:
			material = item_material[item]
			if material not in material_sums:
				material_sums[material] = ({'sum_buy': 0, 'sum_sell': 0})
			material_sums[material]['sum_buy'] += sum_buy
			material_sums[material]['sum_sell'] += sum_sell
		else:
			nonmaterial_sum_buy += sum_buy
			nonmaterial_sum_sell += sum_sell
		
		total_sum_buy += sum_buy
		total_sum_sell += sum_sell
	if args.verbose:
		print('')
	
	if not args.short:
		for material in sorted(material_sums):
			print(_('Material: %s - %s / %s') % ( material_names[material],
			 gold(material_sums[material]['sum_buy']), gold(material_sums[material]['sum_sell'])))
		print(_('Items that are not materials - %s / %s') %
		 (gold(nonmaterial_sum_buy), gold(nonmaterial_sum_sell)))
		print('')
		if not args.verbose:
			for item in gw2api.get_list('items', [largest_single['item'], largest_stack['item']]):
				item_info[item['id']] = item
		if largest_single['item'] > 0:
			print(_('Most valuable single item: %s - %s / %s.') % (item_info[largest_single['item']]['name'],
			 gold(largest_single['sum_buy']), gold(largest_single['sum_sell'])))
		if largest_stack['item'] > 0:
			print(_('Most valuable stack: %s - %d items, %s / %s.') % (item_info[largest_stack['item']]['name'],
			 item_counts[largest_stack['item']], gold(largest_stack['sum_buy']), gold(largest_stack['sum_sell'])))
		if largest_single['item'] > 0 or largest_stack['item'] > 0:
			print('')
	print(_('%s, your storage is worth %s / %s.') % (query['account']['name'],
	 gold(total_sum_buy), gold(total_sum_sell)))

# PSEUDO-I18N
messages = ({'de': {}})

messages['de']['Analyzing storage of %s...'] = u'Analysiere Lager von %s...'
messages['de']['Adding %s - %d items, %s / %s'] = u'Füge %s hinzu - %d Gegenstände, %s / %s'
messages['de']['Material: %s - %s / %s'] = u'Material: %s - %s / %s'
messages['de']['Items that are not materials - %s / %s'] = u'Gegenstände, die keine Materialien sind - %s / %s'
messages['de']['Most valuable single item: %s - %s / %s.'] = u'Wertvollster Einzelgegenstand: %s - %s / %s.'
messages['de']['Most valuable stack: %s - %d items, %s / %s.'] = u'Wertvollster Stapel: %s - %d Stück, %s / %s.'
messages['de']['%s, your storage is worth %s / %s.'] = u'%s, dein Lager hat einen Wert von %s / %s.'

def _(text):
	if config['language'] in messages:
		if text in messages[config['language']]:
			return messages[config['language']][text]
	return text

# MAIN
import argparse
argparser=argparse.ArgumentParser(description='''Compute the value of items lying around in your bank/materials
 storage and materials in your character's inventories. Value output is (Maximum buy offer / maximum sell offer).
 This is only a rough value and does not count in taxes or the amount of offers.''')
argparser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
 help='Output more info while adding up')
argparser.add_argument('-s', '--short', dest='short', action='store_true',
 help='Only output the sum line, no other information.')
argparser.add_argument('profile', default='default', nargs='?', metavar='PROFILE', help='Profile in INI file')
args = argparser.parse_args()

config = gw2api.init(args.profile)

main()
