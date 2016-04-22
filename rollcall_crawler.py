'''
Grab roll call results from voteview.com.
TODO: rewrite as wget/sed?
'''

import requests
import argparse
import re
try:
    import cPickle as pickle
except ImportError as e:
    import pickle
import sys
from urlparse import urljoin
import os.path
import urllib
from time import sleep

from bs4 import BeautifulSoup


_root = 'http://voteview.com'
_site = 'http://voteview.com/dwnl.htm'
_text_target = re.compile('\.ord$')
_stata_target = re.compile('\.dta$')
_targets = [ _text_target, _stata_target ]
_default_save_dir = 'roll_call_data'


def _setup_save_dir(save_dir):
    if not os.path.exists(save_dir):
        try:
            os.mkdir(save_dir)
        except Exception as e:
            sys.exit('Unable to create save location {}.'.format(save_dir))


def _save_ref(ref, save_dir):
    file_ = ref[ref.rfind('/')+1:]
    #r = requests.get(ref)
    #with open(os.path.join(save_dir, file_)) as output:
        #output.write(r.content)
    urllib.urlretrieve(ref, os.path.join(save_dir, file_))



def get_roll_call(roll_call_element, save_dir):
    r = requests.get(urljoin(_root, roll_call_element.get('href')))
    if r.status_code != requests.codes.ok:
        print('bad page level request: {}'.format(r.status_code))
    soup = BeautifulSoup(r.content, 'lxml')
    links = soup.find_all('a')

    for link in links:
        ref = link.get('href')
        # TODO: list/method
        for target in _targets:
            if target.search(ref):
                print('Grabbing: {}'.format(ref))
                _save_ref(ref, save_dir)


def get_roll_calls(start, end, save_dir):
    # TODO: rewrite as nicer filter.
    top = requests.get(_site)
    if top.status_code != requests.codes.ok:
        print('bad top level request: {}'.format(top.status_code))
    soup = BeautifulSoup(top.content, 'lxml')
    _setup_save_dir(save_dir) 
    candidates = soup.find_all('a', string=re.compile('.*Roll Call.*'))
    
    start_year_re = re.compile('^[0-9]+')
    for candidate in candidates:
        match = start_year_re.match(candidate.text)
        if match:
            try:
                year = int(match.group())
                if year >= start and year <= end:
                    get_roll_call(candidate, save_dir)
                    sleep(12)
            except Exception as e:
                # TODO: useful information.
                print(candidate, e.message, e.args)


def main():
    parser = argparse.ArgumentParser(description='todo')
    parser.add_argument('--start', type=int, help='First congress to fetch (inclusive.)')
    parser.add_argument('--end', type=int, help='Last congress to fetch (inclusive).')
    parser.add_argument('--save', type=str, default=_default_save_dir)
    args = parser.parse_args()
    get_roll_calls(args.start, args.end, args.save)


if __name__ == '__main__':
    main()
