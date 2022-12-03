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
#All important tables here have the class 'dextable', and start with a 'No.' field for dex number, with corresponding data starting with '#'.
#Time to make some strategic decisions. Assume user knows what moves do.
#Limit scope to finding candidates for overlapping learnsets and showing their stats.
#All of the non-obvious variable names draw their definitions from the attached constants.py file.

def get_mons(url):
    LOGGER.info(f"Getting Pokemon from {url}...")
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser') 
    dex_table = soup.find('table',  class_='dextable') #These are the right tables, and all of the right tables.
    rows = dex_table.find_all('tr')
    mons = []
    print(rows)
    # print("CASE 1: \n \n")
    #print(rows[2]) #Let's start simply. This one *only* yields Jigglypuff's data.
   # print("CASE 2: \n \n")
   # print(rows[2:len(rows)]) #A little more complicated now. This one probably goes wrong. Actually, no. It just... only gives four entries.
   # print("CASE 3: \n \n")
   # print(rows[2:len(rows) - 1]) #This one's probably safe but unfulfilling. In truth? Just like CASE 2.
   # print("CASE 4: \n \n")
   # print(rows[2:len(rows) - 1:2]) #Okay, so I'm only getting four entries here. What the hell? The table goes on longer.
   # print ((rows[2]) ==(rows[2:len(rows)]))
   # print((rows[2:len(rows)]) == (rows[2:len(rows) - 1:2]))
    print('Entering FOR loop.')
    for index,row in enumerate(rows[2:len(rows) - 1:2]): #Okay, this is probably the last piece of the puzzle.
        try:
            cols = row.find_all('td')
            num_raw = cols[NUM_IDX].text #This is just '#', followed by the dex number.
            print(len(num_raw))
            print(cols[NUM_IDX].text) 
            #So something happens after the second 088 that stops the later entries from loading on pound? Still not sure what this is.
            mon = {}
            num = ''
            for c in num_raw: #This is checking through the elements of [NUM_IDX] character by character, and adding the digits to form dex numbers.
                print(c)
                if c.isdigit():
                    num += c
            try:
                mon[NUM_KEY] = int(num) #Attempt to render the mon's NUM_KEY as the sequence of digits from num_raw, cast to int.
            except:
                print('Except.')
                print(num_raw)
                mon[NUM_KEY]=num #Attempt to pass the information uncast if casting fails.
            mon[NAME_KEY] = cols[NAME_IDX].find('a').text #This part looks like it'll extract the Pokemon's name appropriately.
            types_tags = cols[TYPES_IDX].find_all('a')
            mon[TYPE_KEY] = []
            for a in types_tags:
                mon[TYPE_KEY].append(a['href'].split('/')[-1])
            #This section below seems to be fine, extracting the base stat values for the Pokemon in question.
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
