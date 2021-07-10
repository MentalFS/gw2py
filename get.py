#!/usr/bin/env python

import gw2api, json, argparse

argparser=argparse.ArgumentParser(description='Get raw json from GW2 API v2')
argparser.add_argument(dest='url', metavar='URL', help='URL')
argparser.add_argument('-p', '--profile', dest='profile', default='default',
 help='Profile in INI file')
args = argparser.parse_args()

config = gw2api.init(args.profile)


print json.dumps(gw2api.get_single(args.url), indent=4);
