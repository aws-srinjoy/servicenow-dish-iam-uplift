#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Richard's html2csv converter
#rbarnes@umn.edu
#

from bs4 import BeautifulSoup
import sys
import csv
import argparse

parser = argparse.ArgumentParser(description='Reads in an HTML and attempts to convert all tables into CSV files.')
parser.add_argument('--delimiter', '-d', action='store', default=',',help="Character with which to separate CSV columns")
parser.add_argument('--quotechar', '-q', action='store', default='"',help="Character within which to nest CSV text")
parser.add_argument('--output', '-o', action='store', default='"',help="Output CSV File")
parser.add_argument('filename',nargs="?",help="HTML file from which to extract tables")
args = parser.parse_args()
print(args)

filename=sys.argv[1]

print(f"Opening file {filename}")
with open(filename) as fp:
  print("Parsing file")
  soup = BeautifulSoup(fp,"html.parser")

  print("Preemptively removing unnecessary tags")
  [s.extract() for s in soup('script')]

  for br in soup.find_all("br"):
     br.replace_with("\n")

  print("CSVing file")
  tablecount = -1
  for table in soup.findAll("table"):
    tablecount += 1
    print("Processing Table #%d" % (tablecount))
    with open(args.output, 'w', newline='') as csvfile:
    #with open(sys.argv[1]+str(tablecount)+'.csv', 'w', newline='') as csvfile:
      fout = csv.writer(csvfile, delimiter=args.delimiter, quotechar=args.quotechar, quoting=csv.QUOTE_MINIMAL)
      for row in table.findAll('tr'):
        cols = row.findAll(['td','th'])
        if cols:
          for x in cols:
            print(str(x.text))
          cols = [str(x.text) for x in cols]
          fout.writerow(cols)
