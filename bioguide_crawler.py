import argparse
import re
import datetime
import os
import os.path
from urlparse import urljoin
import time

import requests
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
    StaleElementReferenceException)


_bioguide_root = 'bioguide.congress.gov/biosearch'
_biosearch_url = urljoin(_bioguide_root, 'biosearch.asp')
_biosearch_results_url = urljoin(_bioguide_root, 'biosearch1.asp')
_default_output = 'crawler_results'



def _setup_headless_browser():
    display = Display(visible=0, dimensions=(800, 600))
    display.start()
    fox = webdriver.Firefox()
    sleep(24)
    return fox, display


def _setup_output_dir(output_root):
    if not os.exists(output_root):
        os.mkdir(output_root)
    results_dir = os.path.join(output_root, str(datetime.date.today()))
    if not os.exists(results_dir):
        os.mkdir(results_dir)
    return os.path.abspath(results_dir)


def _scrape_bioguide(year, output_root):
    # TODO: simple anti-anti scraping delays.
    # TODO: smarter search/supporting other sites
    # TODO: method organization
    browser, display = _setup_headless_browser()
   
    browser.get(_biosearch_url)
    congress_e = browser.find_element_by_name('congress')
    congress_e.click()
    congress_e.send_keys(str(year))
    
    input_elements = browser.find_elements_by_tag_name('input')
    for element in input_elements:
        if element.get_attribute('value') == 'Search':
            element.click()
            break

    names_and_links = [(link.text, link.get_attribute('href') for link in
        browser.find_elements_by_tag_name('a')]

    output_dir = _setup_output_dir(output_root)
    for name, link in names_and_links:
        if name == 'Search Again':
            continue
        else:
            page = requests.get(link)
            with open(os.path.join(output_dir, name), 'w') as output:
                output.write(page.contents) 
        
    browser.quit()
    display.close()


def main():
    parser = argparse.ArgumentParser(
        description='Simple scraper for gathering info on members of congress.')
    # TODO: better descriptions
    parser.add_argument('year', type=int, help='Target lookup year.')
    parser.add_argument('--output', type=str, default=_default_output,
        help='Root output directory.')
    args = parser.parse_args()
    
    _scrape_bioguide(args.year, args.output) 


if __name__ == '__main__':
    main()
