#!/usr/bin/python2.7 -tt
import os
import sys
import argparse
import random
sys.path.append("..")
from metaMorpher_utils import *

# everything tested, works fine
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("chromosome", help="path to chromosome directory")
	args = parser.parse_args()
	rc = RandChrom(args.chromosome)
	return rc.retval

class RandChrom(object):
	def __init__(self, chromd):
		self.chrom_dir = chromd
		self.chroms = [] # list, set by _read_dir
		self.chrom = None # the randomly selected chromosome
		if os.path.isfile(self.chrom_dir):
			self.chroms.append(self.chrom_dir)
		else:
			self._read_dir()
		self.retval = self._get_rand_chrom()
	
	def _read_dir(self):
		'''put chromosomes in directory into list'''
		directory = os.path.abspath(self.chrom_dir)
		for file_ in os.listdir(directory):
			file_ = directory + "/" + file_ # make sure you get the correct abs path
			if os.path.isdir(file_) or file_.endswith("README"): # skip sub directories (there should be none) and README's
				continue
			self.chroms.append(file_)

	def _get_rand_chrom(self):
		'''print chromosome, position to insert and return as tuple'''
		i = random.randint(0, len(self.chroms)-1)
		self.chrom = self.chroms[i]
		genome = ""
		with open(self.chrom, 'r') as thechrom:
			for line in thechrom:
				line = line.strip()
				if line.startswith('>'):
					continue
				genome += line
		j = random.randint(0, len(genome)-1)
		print "chromosome:", self.chrom
		print "position to insert:", j
		return (self.chrom, j)

if __name__ == '__main__':
    main()
