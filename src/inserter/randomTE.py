#!/usr/bin/python2.7 -tt
import os
import sys
import argparse
import random
sys.path.append("..")
from metaMorpher_utils import *

'''
Input:  TE file
Output: string (the TE to be inserted)
'''

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("TE", help="transposable element file")
	args = parser.parse_args()
	rte = RandomTE(args.TE)

class RandomTE(object):
	def __init__(self, te_file):
		self.te_file = te_file
		self.tes = {} # dictionary of te name : base pairs

		self.read_in_tes()
		self.selected_te = self.pick_te()

	def read_in_tes(self):
		value = ""
		key = ""
		with open(self.te_file, 'r') as thefile:
			key = thefile.readline()
			key = key.strip()
			for line in thefile:
				line = line.strip()
				if line.startswith(">"):
					self.tes[key] = value
					key = line[1:]
					value = ""
				else: # accumulate value
					value += line
	
	def pick_te(self):
		'''pick a random transposable element, print it, and return it'''
		keys = self.tes.keys()
		i = random.randint(0, len(keys)-1)
		key = keys[i]
		print key
		print ""
		print self.tes[key]
		return key

if __name__ == '__main__':
    main()
