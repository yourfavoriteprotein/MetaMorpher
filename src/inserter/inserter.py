#!/usr/bin/python2.7 -tt
import os
import sys
import argparse
sys.path.append("..")
from metaMorpher_utils import *

'''
Input:  -Transposable Element (TE) string
		-Chromosome (path to file)
		-position of insert (int)
		-number of repeats (int)

Output: -modified chromosome
'''

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--TE", help="transposable element file", required=True)
	parser.add_argument("--chrom", help="chromosome file", required=True)
	parser.add_argument("--insert", help="insertion position", type=int, required=True)
	parser.add_argument("--repeats", help="number of repeats", type=int, required=True)
	args = parser.parse_args()

	# and now read in and write modified chromosome
	ins = Inserter(args)

class Inserter(object):
	def __init__(self, args):
		self.inFile = args.chrom
		self.te = args.TE
		self.insert = args.insert
		self.repeats = args.repeats
		if self.repeats <= 0:
			print "invalid number of repeats, repeating 1 times"
			self.repeats = 1 
		self.header = "" # set by _open_chromosome
		self.genome = "" # set by _open_chromosome
						 # becomes the modified chromosome in _insert_TE

		self._open_chromosome()
		self._insert_TE()
		self._write_chrom()
	
	def _open_chromosome(self):
		'''read in chromosome file'''
		with open(self.inFile, 'r') as fileIn:
			self.header = fileIn.readline().strip()
			self.genome = fileIn.readlines()
			self.genome = [line.strip() for line in self.genome]
			self.genome = "".join(self.genome)
			'''
			for line in fileIn:
				if line.startswith(">") and not self.header:
					self.header = line[1:]
				self.genome += line.strip()
			'''

	def _insert_TE(self):
		'''insert TE repeats # of of times'''
		newChrom = self.te * self.repeats
		newChrom = self.genome[0:self.insert] + newChrom + self.genome[self.insert:]
		self.genome = newChrom

	def _write_chrom(self):
		'''write modified chromosome to file'''
		fname = self.inFile.split('/')
		fname[-1] = "modified__" + fname[-1] # should have fasta extension
		fname = fname[-1]
		#with open ("modifiedChromosome.fasta", 'w') as outfile:
		with open (fname, 'w') as outfile:
			outfile.write(self.header+"\n")
			for i in xrange(0, len(self.genome), 50):
				outfile.write(self.genome[i:i+50]+"\n")

if __name__ == '__main__':
    main()
