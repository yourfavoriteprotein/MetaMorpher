#!/usr/bin/python -tt

import sys
import argparse
import re
from metaMorpher_utils import *

def main():
	parser = get_PSLCoverage_parser()
	args = parser.parse_args()

	pc = PSLCoverage(args.align, args.query, args.target, args.misassembly, args.mismatch)

	# print out statistics
	pc.coverage_report()

	# not really correct, just to get some output while developing:


class PSLCoverage(object):
	'''
	Takes .psl, contigs, and reference genome as input and calculates % coverage.
	Coverage is the % of reference genome that contigs, the output of an assembler span
	'''

	def coverage_report(self):
		'''print out coverage stats'''
		result = ""
		ctr = 0
		#if self._mismatch:
		for matched in self.reference.matched:
			if matched:
				ctr += 1
		foo = float(ctr)/len(self.reference.matched) * 100
		res = "% matched:", foo
		result += res + '\n'
		print res

		# print % seen
		ctr = 0
		for seen in self.reference.seen:
			if seen:
				ctr += 1
		foo = float(ctr)/len(self.reference.matched) * 100
		res = "% seen:", foo
		result += res + '\n'
		print res

		res =  "# misassembled:", self.misassemblies
		result += res + '\n'
		print res

		if self._count_misassembly:
			res = "Misassembled contigs:"
			result += res + '\n'
			print res
			for contig in self.contigs:
				if self.contigs[contig].misassembled:
					res = "\t", contig
					result += res + '\n'
					print res
		
		result += "\n"
		return result

	def __init__(self, psl, contigs, reference, misassembly=False, quast=False, mismatch=False, block=500):
		# handle passed in args
		self._psl_file = psl						# text file
		self._contig_file = contigs					# text file
		self._reference_file = reference			# text file
		
		self._count_misassembly = misassembly		# boolean
		self._quast = quast							# boolean
		self._mismatch = mismatch					# boolean
		if not block:
			block = 500
		self._minblock = int(block)

		# set instance variables
		self.coverage = 0
		self.misassemblies = 0 # number of misassemblies, to be set later

		# reference data: 
			# reference.genome :	the whole reference as a string; no whitespace or 
			#						comments
			# reference.matched :	bool list, false for each position not matched
			# reference.seen :		bool list, false for each position not seen
		self.reference = None 
		self.refName = None

		# contig data:
			# contigs:	dictionary, saves the "best" contig out of all with same name
			#		ex: contigs = {"contig_1": "aaagtctg", "contig_2": "gtcgtaaa" ...}
		self.contigs = {}

		# psl data:
			# to be completed
		self.psl = {}

		# read in files
		self.read_in_reference()
		self.read_in_contigs()

		#thing = "self.contigs['"
		#for foo in self.contigs:
			#print foo , ":", eval(thing+foo+"'].genome"), "\n\t", eval(thing+foo+"'].matched"), "\n\t", eval(thing+foo+"'].seen")

		self.read_in_psl()
		'''
		for foo in self.psl:
			for bar in self.psl[foo]:
				print bar.qName
				print bar.matches
		'''

		# and now the computations
		self.compute_coverage()


	def read_in_reference(self):
		'''read reference genome into memory'''

		if not is_fasta(self._reference_file):
			# TODO: fastq
			print "not a fasta: " + self._reference_file
			
		with open(self._reference_file, 'r') as ref:
			tmp = ref.readline()
			tmp = tmp[1:]
			tmp = tmp.split()
			self.refName = tmp[0]
			# self.refName = self.refName.strip()
			# self.refName = self.refName[1:].strip() # strip after >

			self.reference = ReferenceGenome(ref.read(-1))

	def read_in_contigs(self):
		'''read contigs into memory'''

		if not is_fasta(self._contig_file):
			# TODO: fastq
			print "not a fasta: " + self._contig_file

		with open(self._contig_file, 'r') as cont_file:
			key = ''
			value = ''
			#key = cont_file.readline()[1:].strip()
			#value = cont_file.readline().strip()
			for line in cont_file:
				if not line.startswith('>'):
					# if it's not a comment (startswith >), it's genome sequence
					value += line.strip()
				else:
					self.contigs[key] = ContigGenome(value)
					key = line[1:].strip().split()
					key = key[0]
					value = ''
			else:
					self.contigs[key] = ContigGenome(value)

		# the first thing we put in was ''
		# we could have used the commented lines below value = '', but this way
		# is better because it strips any leading blank lines from the file.
		# in other words, don't assume the first 2 lines are valid.
		del(self.contigs[''])

	def read_in_psl(self):
		'''
		read psl file into memory
		Will store entire file. Use get_best_contig from metaMorpher_utils to extract
		the best alignment
		'''

		if not is_psl(self._psl_file):
			print "not a psl: " + self._psl_file
		
		with open(self._psl_file, 'r') as psl_file:
			# read past comment lines...
			while not psl_file.readline().strip().startswith('-----'): pass
			for line in psl_file:
				psl = PSLData(line)
				#if not psl.tName in self.refName: # psl output truncates name on whitespace
				if psl.tName != self.refName: # psl output truncates name on whitespace
					continue
				# self.psl[qName] = list of PSLData
				self.psl.setdefault(psl.qName, []).append(psl)

	def compute_coverage(self):
		# go through each contig, keys for self.contigs and self.psl should match

		'''
		for x in self.psl:
			print x
		exit(0)
		'''
		for contig_name in self.contigs: # keyError -- blat might not align each contig (some are very small)
			if not contig_name in self.psl:
				continue
		#for contig_name in self.psl:
			# go through each block, by index i

			#print "test"
			#print self.psl[contig_name]
			#for f in self.psl[contig_name]:
				#print f.qName
			'''
			mis_result = self.contigs[contig_name].misassembled
			if not mis_result:
				is_misassembled(self.psl[contig_name], self._minblock)
			'''
			# number of misassemblies in this contig == num_misassemblies
			mis_result = is_misassembled(self.psl[contig_name], self._minblock)
			num_misassemblies = 0
			if mis_result:
				for misType in mis_result:
					#if "expanded repeat" in misType:
					tmp = misType
					indx = tmp.index("|")
					num_misassemblies += int(tmp[1 + indx:])
					#else:
					#	num_misassemblies += 1

				# for each contig object, set its "misassembled" flag if it is misassembled
				print contig_name, "is misassembled", mis_result
				self.contigs[contig_name].misassembled = True
				#self.misassemblies += 1 # increment number of misassemblies
				self.misassemblies += num_misassemblies # increment number of misassemblies

			for i in xrange(get_best_contig(self.psl[contig_name]).blockCount):
				#if not self.contigs[contig_name].misassembled:
				#if self._count_misassembly or not self.contigs[contig_name].misassembled:
				misassembled = self.contigs[contig_name].misassembled
				if misassembled and self._count_misassembly or not misassembled:
					if self._mismatch:
						# mark all matched
						self._mark_all_matched(contig_name, i) # also marks seen
					else:
						# only mark matched matched
						self._mark_only_matched(contig_name, i) # also marks seen
				# else:
					# don't mark matched
					# don't mark seen
	
	def _mark_all_matched(self, contig_name, block_index):
		'''
		Sets reference.matched and reference.seen True for all bp in the block.
		The block is psl[contig_name].blockWhatever[block_index]
		'''
		# don't care what contig string is

		# get reference (target) start position and size of "current" block
		psl = get_best_contig(self.psl[contig_name])
		tStart = psl.tStarts[block_index]
		blockSize = psl.blockSizes[block_index]

		# mark each position of reference genome in block matched, seen
		self.reference.matched[tStart : tStart + blockSize] = [True]*blockSize
		self.reference.seen[tStart : tStart + blockSize] = [True]*blockSize

	def _mark_only_matched(self, contig_name, block_index):
		'''
		Sets reference.matched and reference.seen True for only bp that match, ex. 
		if the contig's bp is 'A', then it matches if the reference's bp is 'A'.
		'N' will also match because it means any bp.

		The block is psl[contig_name].blockWhatever[block_index]
		'''

		psl = get_best_contig(self.psl[contig_name])
		tStart = psl.tStarts[block_index] # reference
		#tStart = psl.tStart # reference << -- I think these give the same thing
		qStart = psl.qStarts[block_index] # contig
		blockSize = psl.blockSizes[block_index]

		# set every bp we saw to "seen"
		self.reference.seen[tStart : tStart + blockSize] = [True]*blockSize

		# need to grab contig string
		query = self.contigs[contig_name].genome
		target = self.reference.genome
		if psl.strand == '-':
			query = minus_strand(query)

		for i in xrange(0, blockSize): #TODO: make sure I'm not getting off-by-one's
			'''
			q = query[i + qStart]
			try:
				t = target[i + tStart] # errors
			except:
				print psl.tName
				print psl.qName
				print "query, size:", query
				print len(query)
				print "target tStart:", tStart
				print len(target)
				print "blockSize:", blockSize
				exit(0)
			'''
			if query[i + qStart] == target[i + tStart]:
				# they match
				self.reference.matched[i + tStart] = True
			elif query[i + qStart] == 'N' or target[i + tStart] == 'N':
				# they also match (2 cases for readability)
				self.reference.matched[i + tStart] = True

if __name__ == "__main__":
	main()
