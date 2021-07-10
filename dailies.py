#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gw2api
import json #TODO debug

def main():
	dailies = gw2api.get_single(
	 "achievements/daily/tomorrow" if args.tomorrow else "achievements/daily")
	print(json.dumps(dailies, indent=4));

# PSEUDO-I18N
messages = ({'de': {}})
messages['de']['Today\'s Dailies'] = 'Heutige Dailies'
messages['de']['Tomorrow\'s Dailies'] = 'Morgige Dailies'

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
argparser.add_argument('profile', default='default', nargs='?', metavar='PROFILE',
 help='Profile in INI file')
args = argparser.parse_args()

config = gw2api.init(args.profile)

main()
