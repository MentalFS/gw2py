#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gw2api, json, argparse

argparser=argparse.ArgumentParser(description='Get raw json from GW2 API v2')
argparser.add_argument(dest='url', metavar='URL', help='URL',
 nargs='?', default='../v2.json')
argparser.add_argument('-p', '--profile', dest='profile', default='default',
 help='Profile in INI file')
argparser.add_argument('-s', '--schema', dest='schema', default='latest',
 help='Schema version (UTC ISO8601 timestamp)')
args = argparser.parse_args()

config = gw2api.init(args.profile, args.schema)


print(json.dumps(gw2api.get_single(args.url), indent=4));
