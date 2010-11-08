#!/usr/bin/env python
# encoding: utf-8
"""
uploader.py

Created by Abe Epton on 2010-11-07.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.

Uploads every entry from a CSV file to an AppEngine app.
"""

import sys
import os
import urllib
import urllib2

def main():
    FH = open('trans_to_upload.csv', 'r')
    text = FH.readlines()
    FH.close()
    counter = 0
    for line in text:
        quote_locations = []
        index = 0
        while index < len(line):
            if line[index] == '"':
                quote_locations.append(index)
            index += 1
        if len(quote_locations) % 2:
            print 'Unable to decode line: %s' % line
            continue
        index = 0
        quote_tuples = []
        while index < len(quote_locations):
            new_tuple = (quote_locations[index], quote_locations[index + 1])
            quote_tuples.append(new_tuple)
            index += 2
        index = 0
        while index < len(quote_tuples) - 1:
            i = quote_tuples[index][0]
            while i < quote_tuples[index][1]:
                if line[i] == ',':
                    line[i] == '|'
                i += 1
            index += 1
        line.replace('"', '')
        split_line = line.split(',')
        for split in split_line:
            split = split.replace('|', ',')
        if len(split_line) != 7:
            print 'NOT 7 FIELDS - %d: %s' % (len(split_line), split_line)
            counter += 1
            #continue
        entry = {'quote_text': split_line[5], 'quote_text_alt': split_line[6],
                 'person_name': split_line[1], 'location_lat': split_line[3], 
                 'location_long': split_line[4], 'person_age': split_line[2]}
        entry['photo_url'] = 'http://www.flickr.com/photos/40397925@N00/5152835892/in/set-72157625202695917/'
        entry['use_first_question'] = "True"
        entry['audio_url'] = 'http://nothing.com'
        formatted_entry = urllib.urlencode(entry)
        try:
            request = urllib2.Request('http://tenderneeds.appspot.com/add_data',
                                      formatted_entry)
            connection = urllib2.urlopen(request)
            print connection.read()
        except:
            print entry

if __name__ == '__main__':
    main()

