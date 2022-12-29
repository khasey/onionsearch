#!/usr/bin/python3

import argparse
import csv
import math
import re
import time
from datetime import datetime
from functools import reduce
from random import choice
from multiprocessing import Pool, cpu_count, current_process, freeze_support
from tqdm import tqdm
import subprocess

import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import unquote
from bs4 import BeautifulSoup
from urllib3.exceptions import ProtocolError
# from urlparse import urlparse

ENGINES = {
    "ahmia": "https://ahmia.fi",
    "onionsearchserver": "http://3fzh7yuupdfyjhwt3ugzqqof6ulbcl27ecev33knxe3u7goi3vfn2qqd.onion",
    "torgle": "http://no6m4wzdexe3auiupv2zwif7rm6qwxcyhslkcnzisxgeiw6pvjsgafad.onion",
}

desktop_agents = [
    'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0',  # Tor Browser for Windows and Linux
    'Mozilla/5.0 (Android 10; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0',  # Tor Browser for Android
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
    'AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
]

supported_engines = ENGINES

available_csv_fields = [
    "engine",
    "name",
    "link",
    "domain"
]


def print_epilog():
    epilog = "Available CSV fields: \n\t"
    for f in available_csv_fields:
        epilog += " {}".format(f)
    epilog += "\n"
    epilog += "Supported engines: \n\t"
    for e in supported_engines.keys():
        epilog += " {}".format(e)
    return epilog


parser = argparse.ArgumentParser(epilog=print_epilog(), formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--proxy", default='localhost:9050', type=str, help="Set Tor proxy (default: 127.0.0.1:9050)")
parser.add_argument("--output", default='output_$SEARCH_$DATE.txt', type=str,
                    help="Output File (default: output_$SEARCH_$DATE.txt), where $SEARCH is replaced by the first "
                         "chars of the search string and $DATE is replaced by the datetime")
parser.add_argument("--continuous_write", type=bool, default=False,
                    help="Write progressively to output file (default: False)")
parser.add_argument("search", type=str, help="The search string or phrase")
parser.add_argument("--limit", type=int, default=0, help="Set a max number of pages per engine to load")
parser.add_argument("--engines", type=str, action='append', help='Engines to request (default: full list)', nargs="*")
parser.add_argument("--exclude", type=str, action='append', help='Engines to exclude (default: none)', nargs="*")
parser.add_argument("--fields", type=str, action='append',
                    help='Fields to output to csv file (default: engine name link), available fields are shown below',
                    nargs="*")
parser.add_argument("--field_delimiter", type=str, default=",", help='Delimiter for the CSV fields')
parser.add_argument("--mp_units", type=int, default=(cpu_count() - 1), help="Number of processing units (default: "
                                                                            "core number minus 1)")

args = parser.parse_args()
proxies = {'http': 'socks5h://{}'.format(args.proxy), 'https': 'socks5h://{}'.format(args.proxy)}
filename = args.output
field_delim = ","
if args.field_delimiter and len(args.field_delimiter) == 1:
    field_delim = args.field_delimiter


def random_headers():
    return {'User-Agent': choice(desktop_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

def has_git_root(url):
      # Utilise le navigateur TOR comme proxy
  proxy = {
    'http': 'socks5://localhost:9050',
    'https': 'socks5://localhost:9050'
  }

  # Exécute la commande git ls-files en utilisant le proxy
  result = subprocess.run(['git', 'ls-files'], cwd=url, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'http_proxy': proxy['http'], 'https_proxy': proxy['https']})

  # Si la commande a réussi, cela signifie que le répertoire .git existe
  return result.returncode == 0

urls = [
  'http://example1.onion/.git',
  'http://example2.onion/.git',
  'http://example3.onion/.git'
]

for url in urls:
  if has_git_root(url):
    print(f'Le site {url} a un répertoire .git à la racine.')
  else:
    print(f'Le site {url} n\'a pas de répertoire .git à la racine.')



