#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gw2api
from termcolor import colored

def main():
	worlds_path='worlds?ids=all'
	matches_path='wvw/matches?ids=all'

	world_info = gw2api.get_multi(['account', worlds_path, matches_path]);
	own_world = world_info['account']['world']
	own_color = None

	match_filter = lambda match: True
	if own_world >= 1000 and own_world < 2000:
		match_filter = lambda match: match['id'].startswith('1')
	if own_world >= 2000 and own_world < 3000:
		match_filter = lambda match: match['id'].startswith('2')

	world_names = {}
	worlds_by_color = {}
	worlds_by_color['green'] = []
	worlds_by_color['blue'] = []
	worlds_by_color['red'] = []
	for world in world_info[worlds_path]:
		world_names[world['id']] = world['name']
	output_break = False
	
	for match in sorted(world_info[matches_path], key=lambda match: match['id']):
		if not match_filter(match):
			continue
		
		if args.all and output_break: print()
		output_break = True

		is_own_match = False
		if 'all_worlds'	in match:
			worlds_by_color['green'].extend(match['all_worlds']['green'])
			worlds_by_color['red'].extend(match['all_worlds']['red'])
			worlds_by_color['blue'].extend(match['all_worlds']['blue'])
			for color in match['all_worlds']:
				if own_world in match['all_worlds'][color]:
					is_own_match = True
					own_color = color

		if not match['worlds']['green'] in worlds_by_color['green']:
			worlds_by_color['green'].append(match['worlds']['green'])
		if not match['worlds']['red'] in worlds_by_color['red']:
			worlds_by_color['red'].append(match['worlds']['red'])
		if not match['worlds']['blue'] in worlds_by_color['blue']:
			worlds_by_color['blue'].append(match['worlds']['blue'])
		for color in match['worlds']:
			if own_world == match['worlds'][color]:
				is_own_match = True
				own_color = color
			
		if args.all or is_own_match:
			print("=== %s %s (%s) ===" % (_('Matchup'), match['id'], match['start_time'][:10]))
			print("  ", colored(world_names[match['worlds']['green']], 'green'), end=' ')
			if 'all_worlds'	in match:
				for world in match['all_worlds']['green']:
					if world != match['worlds']['green']:
						print("+", colored(world_names[world], 'green'), end=' ')
			print("(%s)" % match['scores']['green'])
			print("vs", colored(world_names[match['worlds']['red']], 'red'), end=' ')
			if 'all_worlds'	in match:
				for world in match['all_worlds']['red']:
					if world != match['worlds']['red']:
						print("+", colored(world_names[world], 'red'), end=' ')
			print("(%s)" % match['scores']['red'])
			print("vs", colored(world_names[match['worlds']['blue']], 'cyan'), end=' ')
			if 'all_worlds'	in match:
				for world in match['all_worlds']['blue']:
					if world != match['worlds']['blue']:
						print("+", colored(world_names[world], 'cyan'), end=' ')
			print("(%s)" % match['scores']['blue'])

	
	if args.color:
		if args.all or own_color == 'green':
			print()
			print("===", colored(_('Green worlds'), 'green'), "===")
			for world in sorted(worlds_by_color['green']):
				print(world_names[world])
		if args.all or own_color == 'red':
			print()
			print("===", colored(_('Red worlds'), 'red'), "===")
			for world in sorted(worlds_by_color['red']):
				print(world_names[world])
		if args.all or own_color == 'blue':
			print()
			print("===", colored(_('Blue worlds'), 'cyan'), "===")
			for world in sorted(worlds_by_color['blue']):
				print(world_names[world])

# PSEUDO-I18N
messages = ({'de': {}})
messages['de']['Matchup'] = 'Zuordnung'
messages['de']['Green worlds'] = 'Grüne Welten'
messages['de']['Red worlds'] = 'Rote Welten'
messages['de']['Blue worlds'] = 'Blaue Welten'

def _(text):
	if config['language'] in messages:
		if text in messages[config['language']]:
			return messages[config['language']][text]
	return text

# MAIN
import argparse
argparser=argparse.ArgumentParser(description='List the current WvW matches.')
argparser.add_argument('-a', '--all', dest='all', action='store_true',
 help='List info for all worlds.')
argparser.add_argument('-c', '--color', dest='color', action='store_true',
 help='List info for worlds by color.')
argparser.add_argument('profile', default='default', nargs='?', metavar='PROFILE',
 help='Profile in INI file')
args = argparser.parse_args()

config = gw2api.init(args.profile)

main()
