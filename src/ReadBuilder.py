#!/usr/bin/python -tt

import sys
import argparse
import random
import os
import re

import metaMorpher_utils as mu

def main():
	parser = mu.get_ReadBuilder_parser()
	args = parser.parse_args()

	# create new ReadBuilder object
	rb = ReadBuilder(args.target, args.insert, args.error, args.reads, args.readsize,
		args.file1, args.file2, args.seed, args.multiple)
	rb.make_reads()

class ReadBuilder(object):
	'''object intended to create reads from input file'''
	def __init__(self, target, insert_size=300, error_rate=0, number_reads=100, read_size=100, file1="file1.fasta", file2="file2.fasta", seed=None, mc=False):
		'''
		initialize ReadBuilder. File is not optional, all other fields are
		-insert_size: 300 bp default
		-error_rate: 0% default. Accepts an integer argument
		-number_reads: 100 default. How many reads there will be
		-file1, file2: the names of the output fasta files
		'''
		self._target = target
		self._insert = insert_size
		self._error = error_rate
		self._num_reads = number_reads
		self._read_size = read_size
		self._file1 = file1
		self._file2 = file2
		self._multiple_chrom = mc

		if not os.path.exists(self._target):
			raise Exception("File not found: %s" % self._target)

		# since we're opening files to append, want to remove contents of file1,2
		if os.path.isfile(self._file1):
			os.remove(self._file1)
		if os.path.isfile(self._file2):
			os.remove(self._file2)

		self.rand = random.Random() # instance of Random object
		self.nucleotides = "a t g c".split()
		self.alt_nucleotides = "n ".split()

		if seed:
			self.rand.seed(seed)

		#self.make_reads()

	def make_reads(self):
		'''
		driver for _make_single_reads -- call it multiple times if there are multiple
		chromosomes or just once if there is a single chromosome
		'''

		if self._multiple_chrom: # multiple chromosomes -- iterate over files in directory
			directory = self._target[:]
			i = j = 0
			for file_ in os.listdir(directory):
				file_ = directory + "/" + file_ # make sure you get the correct rel path
				if os.path.isdir(file_): # skip sub directories (there should be none)
					continue
				self._target = file_
				i, j = self._make_single_reads(i, j)

		else:
			# just make one read
			self._make_single_reads()
		
	def _make_single_reads(self, start1=0, start2=0):
		'''
		Open file for reading, create output fasta files with specified insert size,
		error rate, and number of reads. See usage message for optional parameters.

		returns tuple (num1, num2), where num1 is #lines in file1, num2 is #lines in file2
		'''

		# open files
		out1 = open(self._file1, "a") # open file to append
		out2 = open(self._file2, "a") # why not overwrite? if you want multiple chromosomes
		target = open(self._target, "r")

		# read in entire file as single string:
		all_lines = target.read(-1)

		wspc = re.compile(r"\s")
		nofirstline = re.compile(r">.*\n")

		# remove first line and newline chars from input
		all_lines = re.sub(nofirstline, "", all_lines)
		all_lines = re.sub(wspc, "", all_lines)

		# make #reads copies
		last_pos = len(all_lines) - 1
		outctr1 = start1
		outctr2 = start2
		for iteration in range(0, self._num_reads):
			start_pos = self.rand.randint(0, last_pos-1) # don't want case: no bp printed
			mate_pos = start_pos + self._insert

			# create reads from start_pos to EOF
			for curr_pos in range(start_pos, last_pos+1, self._read_size):
				if start_pos < last_pos:
					out1.write(">read %d/1\n" % outctr1)
					outctr1 += 1
				out1.write(self.get_char(all_lines[curr_pos : curr_pos + self._read_size]))
				out1.write("\n")

			# create associated paired ends
			# write output to string, then reverse it
			out2string = ''
			for curr_pos in range(mate_pos, last_pos+1, self._read_size):
				out2string = self.get_char(all_lines[curr_pos : curr_pos + self._read_size])
				if out2string:
					out2.write(">read %d/2\n" % outctr2)
					outctr2 += 1
					out2.write(out2string[::-1]+'\n')

		# close the files
		out1.close()
		out2.close()
		target.close()

		# return counters
		return outctr1, outctr2
	
	def get_char(self, inputString):
		'''
		pass a string of length to get_char
		get_char returns a string with each char having error_rate % chance of being
		a different base pair
		'''

		if self._error == 0:
			return inputString

		inputString = inputString.lower()
		result = ''

		for bp in inputString:
			# if it's not valid, complain and die
			if not bp in self.nucleotides and not bp in self.alt_nucleotides:
				raise Exception("Invalid base pair passed to get_char: %s" % bp)
			if self._error <= self.rand.randint(0,99):
				result += bp
			else:
				nucs = self.nucleotides[:]
				del(nucs[nucs.index(bp)])
				result += nucs[self.rand.randint(0,2)]

		return result

if __name__ == "__main__":
		main()
