#!/usr/bin/python3
"""
This module scrapes the Scarlet/Violet Attackdex on Serebii to try and find learnsets for a given move.
"""

import csv
import json
import logging
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from constants import *
import requests

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


PARSER = ArgumentParser(description='Pokemon scraper that pulls the learnset for move specified in argument from Serebii.')
PARSER.add_argument('-o', '--output', action='store', help='Saves the results to an output .json file.')
ARGS = PARSER.parse_args()

#Later version of this code should take a pair of user inputs and cross-reference the specified moves' learnsets for a match.

#Taking a moment here to analyze the structure of the Serebii moveset pages more closely...
#The important stuff is in the 'content' div, specifically under the 'main' tag, but not everything under the 'main' tag.
#The good stuff is going to be in a table with class 'dextable'. 
#What if we try to process *every* dextable that comes up in the attackdex for that page? Junk data that overwhelms the user, more work.
#Time to make some strategic decisions. Assume user knows what moves do.
#Limit scope to finding candidates for overlapping learnsets and showing their stats.
#Deduction - Need to sort through the 'dextables' and only count the ones that start with a dex number field.
#This is fine because every row we care about will start with a dex number field, no matter how the move is taught.
#All dex number fields start with a '#', regardless of whether the dex entry they correspond to has a NatDex number.

def get_mons(url):
    LOGGER.info(f"Getting Pokemon from {url}...")
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser') 
    dex_table = soup.find('table',  class_='dextable')
    rows = dex_table.find_all('tr')
    mons = []
    for index,row in enumerate(rows[2:len(rows) - 1:2]):
        try:
            cols = row.find_all('td')
            print(len(cols))
            print(*cols,  sep = "\n")
            print(NUM_IDX)
            num_raw = cols[NUM_IDX].text
            print(len(num_raw))
            #Okay, so it seems like num_raw is why we're getting four entries. Why is cols[NUM_IDX].text only getting four entries?
            print(cols[NUM_IDX].text) #So something happens after the second 088 that stops the later entries from loading on pound?
            #While I'm thinking about it, how does the code know that column is called NUM_IDX in the first place?
            mon = {}
            num = ''
            for c in num_raw:
                if c.isdigit():
                    num += c
            try:
                mon[NUM_KEY] = int(num) #Need to figure out how these keys and indexes are defined!
            except:
                print(num)
                mon[NUM_KEY]=num
            mon[NAME_KEY] = cols[NAME_IDX].find('a').text
            types_tags = cols[TYPES_IDX].find_all('a')
            mon[TYPE_KEY] = []
            for a in types_tags:
                mon[TYPE_KEY].append(a['href'].split('/')[-1])

            mon[HP_KEY] = int(cols[HP_IDX].text)
            mon[ATK_KEY] = int(cols[ATK_IDX].text)
            mon[DEF_KEY] = int(cols[DEF_IDX].text)
            mon[SPATK_KEY] = int(cols[SPATK_IDX].text)
            mon[SPDEF_KEY] = int(cols[SPDEF_IDX].text)
            mon[SPD_KEY] = int(cols[SPD_IDX].text)
            print(mon)
            mons.append(mon)
        except Exception as ex:
            print(index)
            LOGGER.error(f"Can't parse row {index}. {ex}")
    LOGGER.info(f'Found {len(mons)}.')
    LOGGER.info(f'Done getting Pokemon from {url}.')

    return mons

def write_to_csv(mons, filename):
    with open(filename, 'w', encoding='utf-8', newline = '') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([NUM_KEY, NAME_KEY, TYPE_KEY, HP_KEY, ATK_KEY, DEF_KEY, SPATK_KEY, SPDEF_KEY, SPD_KEY])
        for mon in mons:
            writer.writerow([mon[NUM_KEY], mon[NAME_KEY], mon[TYPE_KEY], mon[HP_KEY], mon[ATK_KEY], mon[DEF_KEY], mon[SPATK_KEY], mon[SPDEF_KEY], mon[SPD_KEY]])

def write_to_json(mons, filename):
    with open(filename, mode='w', encoding='utf-8') as output_file:
        json.dump(mons, output_file, indent=4)

if __name__=='__main__':
    print("Starting execution")
    url_base = 'https://www.serebii.net/attackdex-sv/'
    url = url_base + ARGS.output + '.shtml' #Should take the form of 'movename.shtml'
    print(url)
    mons = get_mons(url)
    if ARGS.output:
        filename = 'path/' + ARGS.output + '.json'
        filetype = filename[filename.rindex('.')+1:]
        try:
            if filetype == 'csv':
                write_to_csv(mons, filename)
            else:
                write_to_json(mons, filename)
        except Exception as ex:
            LOGGER.error(f'Error writing to {filename}. {ex}')
