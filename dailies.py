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

	dailies_endpoint = 'achievements/daily/tomorrow' if args.tomorrow else 'achievements/daily'
	responses = gw2api.get_multi([dailies_endpoint, 'account', 'account/achievements'])
	dailies = responses[dailies_endpoint]
	account = responses['account']
	unlocked = []
	for achievement in responses['account/achievements']:
		if achievement['done']:
			unlocked.append(achievement['id'])

	achievement_ids = []
	for category, entries in dailies.items():
		if args.ignore and category in args.ignore:
			continue
		for daily in entries:
			achievement_ids.append(daily['id'])

	achievements = {}
	item_ids = []
	for achievement in gw2api.get_list('achievements', achievement_ids):
		achievements[achievement['id']] = achievement
		if 'rewards' in achievement:
			for reward in achievement['rewards']:
				if reward['type'] == 'Item':
					item_ids.append(reward['id'])
	items = {}
	if args.verbose:
		for item in gw2api.get_list('items', item_ids):
			items[item['id']] = item

	print(_('Tomorrow\'s Dailies for %s:' if args.tomorrow else
	 'Today\'s Dailies for %s:') % account['name'])
	for category, entries in dailies.items():
		if args.ignore and category in args.ignore:
			continue
		category_name = _(categories[category] if category in categories else category)
		if entries and not args.verbose:
			print('\n== %s ==' % category_name)
		for daily in entries:
			achievement = achievements[daily['id']]
			if 'prerequisites' in achievement:
				for prerequesite in achievement['prerequisites']:
					if not prerequesite in unlocked:
						continue
			if 'required_access' in daily:
				required_product = daily['required_access']['product']
				required_condition = daily['required_access']['condition']
				if not required_product or not required_condition in ['HasAccess', 'NoAccess']:
					raise ValueError(
					 'Unknown required access description: %s' % daily['required_access'])
				if required_condition == 'HasAccess' and not required_product in account['access']:
					continue
				elif required_condition == 'NoAccess' and required_product in account['access']:
					continue

			level_suffix = ''
			min_level = daily['level']['min']
			max_level = daily['level']['max']
			if args.max_level and max_level < 80:
				continue
			if not args.max_level:
				if min_level == max_level:
					level_suffix = ' (%d)' % max_level
				elif min_level != 1 or max_level != 80:
					level_suffix = ' (%d - %d)' % (min_level, max_level)

			name = achievement['name']
			if not args.verbose:
				print('%s%s' % (name, level_suffix))
			else:
				print('\n== %s: %s%s ==' % (category_name, name, level_suffix))
				print(achievement['requirement'])
				if 'rewards' in achievement:
					for reward in achievement['rewards']:
						if reward['type'] == 'Coins':
							print('- %s' % gw2api.format_gold(reward['count']))
						elif reward['type'] == 'Item':
							print('- %d %s' % (reward['count'], items[reward['id']]['name']))
						else:
							print('- %s' % _('Special reward'))



# PSEUDO-I18N
messages = ({'de': {
	'Today\'s Dailies for %s:': u'Heutige Dailies f??r %s:',
	'Tomorrow\'s Dailies for %s:': u'Morgige Dailies f??r %s:',
	'Fractals': u'Fraktale',
	'Special': u'Spezial',
	'Special reward': u'Spezial-Belohnung'
}})
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
argparser.add_argument('-m', '--max-level', dest='max_level', action='store_true',
 help='Only show dailies for level 80.')
argparser.add_argument('-i', '--ignore', dest='ignore', nargs='+',
 help='Ignore categories: pve pvp wvw fractals special')
argparser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
 help='Show description and rewards for each daily.')
argparser.add_argument('profile', default='default', nargs='?', metavar='PROFILE',
 help='Profile in INI file')
args = argparser.parse_args()

config = gw2api.init(args.profile)

main()
