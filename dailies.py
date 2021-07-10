#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gw2api

def main():
	categories = {
		'pve': 'PvE',
		'pvp': 'PvP',
		'wvw': 'WvW',
		'fractals': 'Fractals',
		'special': 'Special'
	}

	dailies = gw2api.get_single(
	 'achievements/daily/tomorrow' if args.tomorrow else 'achievements/daily')

	ids = []
	for category, entries in dailies.items():
		for daily in entries:
			ids.append(daily['id'])

	achievements = {}
	for achievement in gw2api.get_list('achievements', ids): #[d['id'] for d in dailies]):
		achievements[achievement['id']] = achievement

	print('%s:' % _('Tomorrow\'s Dailies' if args.tomorrow else 'Today\'s Dailies'))
	for category, entries in dailies.items():
		if args.ignore and category in args.ignore:
			continue
		category_name = _(categories[category] if category in categories else category)
		if entries and not args.verbose:
			print('\n== %s ==' % category_name)
		for daily in entries:
			name = achievements[daily['id']]['name']
			min_level = daily['level']['min']
			max_level = daily['level']['max']
			if not args.verbose:
				print('%s (%d - %d)' % ( name, min_level, max_level ))
			else:
				print('\n== %s: %s (%d - %d) ==' % ( category_name, name, min_level, max_level ))
				print(achievements[daily['id']]['requirement'])


# PSEUDO-I18N
messages = ({'de': {}})
messages['de']['Today\'s Dailies'] = 'Heutige Dailies'
messages['de']['Tomorrow\'s Dailies'] = 'Morgige Dailies'
messages['de']['Fractals'] = 'Fraktale'
messages['de']['Special'] = 'Spezial'

def _(text):
	if config['language'] in messages:
		if text in messages[config['language']]:
			return messages[config['language']][text]
	return text

# MAIN
import argparse
argparser=argparse.ArgumentParser(description='List the current or upcoming dailies')
argparser.add_argument('-t', '--tomorrow', dest='tomorrow', action='store_true',
 help='List upcoming dailies.')
argparser.add_argument('-i', '--ignore', dest='ignore', nargs='*',
 help='Ignore categories: pve pvp wvw fractals special')
argparser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
 help='Show longer descriptions.')
argparser.add_argument('profile', default='default', nargs='?', metavar='PROFILE',
 help='Profile in INI file')
args = argparser.parse_args()

config = gw2api.init(args.profile)

main()
