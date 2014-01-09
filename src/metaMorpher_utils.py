#!/usr/bin/python -tt

import re
import argparse

#################################################
#												#
#	parsers	-- used in all scripts				#
#												#
#################################################

def get_ReadBuilder_parser(parser=None):
	if not parser:
		parser = argparse.ArgumentParser(description="simulate read/paired end data " \
			"creation with reference genome input")
	parser.add_argument("target", help="Reference genome (file, or dir for multiple " \
		"chromosomes) to create reads from")
	_ReadBuilder_base_parser(parser)

	return parser

def _ReadBuilder_base_parser(parser):
	parser.add_argument("-i", "--insert", help="set the insert size, " \
		"default is 300", type=int, default=300)
	parser.add_argument("-e", "--error", help="set the error rate, " \
		"default is 0%%", type=int, default=0)
	parser.add_argument("-r", "--reads", help="set the number of reads, " \
		"default is 100", type=int, default=100)
	parser.add_argument("-rs", "--readsize", help="set read size " \
		"(number of bp per read); default is 100", type=int, default=100)
	parser.add_argument("-1", "--file1", help="set filename for first read, " \
		"default is 'file1.fasta'", default="file1.fasta")
	parser.add_argument("-2", "--file2", help="set filename for paired end, " \
		"default is 'file2.fasta'", default="file2.fasta")
	parser.add_argument("--seed", help="set random.seed with some integer " \
		"in order to have repeatability", type=int)
	parser.add_argument('-mc', '--multiple', help="create reads from multiple " \
		"chromosomes. \"target\" must be a directory", action='store_true')

	return parser

def get_PSLCoverage_parser(parser=None):
	if not parser:
		parser = argparse.ArgumentParser(description="calculate % of genome " \
			"covered given reference genome, configs generated by assembler, " \
			"and alignment (PSL format)")
	_PSLCoverage_base_parser(parser)

	# required arguments:
	parser.add_argument('-t', '--target', help="[REQUIRED] target input file; " \
		"the reference genome", required=True)
	parser.add_argument('-a', '--align', help="[REQUIRED] alignment input file; " \
		"should be psl format", required=True)
	parser.add_argument('-q', '--query', help="[REQUIRED] query input file; " \
		"the contigs generated by an assembler", required=True)
	parser.add_argument('-qu', '--quast', help="include quast report, defaults " \
		"to false", action='store_true')
	parser.add_argument('--quastpath', help="path to Quast executable")

	return parser

def _PSLCoverage_base_parser(parser):
	# optional arguments:
	parser.add_argument('-mi', '--misassembly', help="include misassemblies in %% " \
		"coverage, defaults to false", action='store_true')
	parser.add_argument('-mm', '--mismatch', help="include mismatched base pairs " \
		"in %% coverage, defaults to false", action='store_true')
	parser.add_argument("--block", help="set minimum block size to be " \
		"considered misassembled, default is 500.")
	return parser

def _noread_base(parser):
	parser.add_argument('-re', "--reads", help="[REQUIRED] the fasta file containing " \
		"reads", required=True)
	parser.add_argument('-pa', '--paired', help="the fasta containing paired ends")
	parser.add_argument('-t', '--target', help="[REQUIRED] target input file; " \
		"the reference genome", required=True)

def _MetaMorpher_base_parser(parser=None):
	if not parser:
		parser = argparse.ArgumentParser(description="MY GREAT PARSER")
	parser.add_argument('--assembler', help="include name of assembler you want to " \
		"use, for example 'Velvet' or 'Ray'. Defaults to Velvet.")
	parser.add_argument('-qu', '--quast', help="include quast report, defaults " \
		"to false", action='store_true')
	parser.add_argument('-k', '--kmer', help="set kmer length, if applicable", type=int)
	parser.add_argument('--assemblerpath', help="path to assembler executable")
	parser.add_argument('--quastpath', help="path to Quast executable")
	parser.add_argument('--blatpath', help="path to Blat executable")
	return parser

def get_MetaMorpher_parser(parser=None):
	# parser arguments:
	setup = "SETUP"
	run = "RUN"
	noread = "noread"
	runall = "runall"
	reads = "readsonly"
	report = "reportonly"

	# parser initialization
	sb = "\033[1m" # bold
	eb = "\033[0;0m" # unbold
	desc = sb+setup+":"+eb+"\t\trun setup to interactively create configuration " \
		"profile\n" \
		+sb+run+":"+eb+"\t\trun script with configuration generated by setup\n" \
		+sb+noread+":"+eb+"\t\tdo not generate simulated reads\n" \
		+sb+runall+":"+eb+"\t\tgenerate simulated reads, run assembler, blat, " \
		"and display report\n" \
		+sb+reads+":"+eb+"\tsimulate reads ONLY\n" \
		+sb+report+":"+eb+"\tdisplay report only, must provide .psl, query and " \
		"target genomes\n\n" \
		"MetaMorpher.py {"+setup+", "+run+", "+noread+", "+runall+", "+reads+", " \
		+report+"} -h \n\t\tfor additional help"

	parser = argparse.ArgumentParser(description=desc,
		formatter_class=argparse.RawTextHelpFormatter)
	subparser = parser.add_subparsers(dest="commands")

	# SETUP parser
	setup_p = subparser.add_parser(setup, description="interactive " \
		"configuration generator") # setup "wizard", run ./MetaMorpher.py setup -h for msg

	# RUN parser
	run_p = subparser.add_parser(run, description="run from saved configuration. " \
		"To create configuration, run " +setup+".")
	run_p.add_argument('--config', help="path to configuration file")

	# noread parser
	noread_p = subparser.add_parser(noread, description="do not generate " \
		"simulated reads; provide reads and paired end fasta files.")
	_noread_base(noread_p) # adds args for reads, paired end, ref. genome
	_MetaMorpher_base_parser(noread_p) # assembler, quast optional args
	_PSLCoverage_base_parser(noread_p) # misassembly, mismatch
	noread_p.add_argument('-mc', '--multiple', help="create reads from multiple " \
		"chromosomes. \"fileIn\" must be a directory", action='store_true')
	
	# runall parser
	runall_p = subparser.add_parser(runall, description="generate simulated reads, " \
		"run assembler, and generate report")
	get_ReadBuilder_parser(runall_p)   # query + optional args
	_MetaMorpher_base_parser(runall_p) # assembler, quast optional args
	_PSLCoverage_base_parser(runall_p) # misassembly, mismatch

	# reads parser
	reads_p = subparser.add_parser(reads, description="generate simulated reads only")
	get_ReadBuilder_parser(reads_p)

	# report parser
	report_p = subparser.add_parser(report, description="display result only, must " \
		"provide .psl, query and target")
	get_PSLCoverage_parser(report_p)
	report_p.add_argument('-mc', '--multiple', help="create reads from multiple " \
		"chromosomes. \"fileIn\" must be a directory", action='store_true')


	# done building sub parsers
	return parser


#################################################
#												#
#	checking file extensions					#
#												#
#################################################

def is_fasta(filename):
	'''return true if file extension indicates file is in FASTA format'''
	fname = filename[:]
	fname = fname.lower()
	if fname.endswith(".fa"):
		return True
	if fname.endswith(".fas"):
		return True
	if fname.endswith(".fasta"):
		return True
	return False

def is_fastq(filename):
	'''return true if file extension indicates file is in FASTQ format'''
	fname = filename[:]
	fname = fname.lower()
	if fname.endswith(".fq"):
		return True
	if fname.endswith(".fastq"):
		return True
	return False

def is_psl(filename):
	'''return true if file extension indicates file is in PSL format'''
	fname = filename[:]
	fname = fname.lower()
	if fname.endswith(".psl"):
		return True
	return False

#################################################
#												#
#	utility functions for PSLCoverage.py		#
#												#
#################################################

def get_best_contig(psl_lst):
	'''extract "best" psl (PSLData object) from list of psl's and return psl object'''
	# For now, return the one with greatest number matches
	def get_matches(psl):
		return psl.matches
	return max(psl_lst, key=get_matches)

def is_misassembled(psl_lst, msize=500):
	'''returns true if contig is misassembled and false otherwise'''

	psls = psl_lst[:]
	best = get_best_contig(psls)
	if best.matches < msize:
		return []
	psls.pop(psls.index(best)) # remove "best" alignment

	# now remove elements with length < 500 bp (default msize)
	res = []
	for psl in psls:
		if psl.matches < msize:
			continue
		res.append(psl)
	else:
		psls = res

	psls3 = psls[:] #used for checking expanded repeats

	final_result = []
	# if there are no alignments after removing ones < 500, no misassembly
	if psls:
		# now test for misassemblies (method 1)
		result =  _method_1(psls, best, msize)
		if result:
			#print "method 1 result:", result
			final_result.extend(result)

	# put "best" alignment back in for method 2
	psls.append(best)

	# prune psls again -- remove alignments without blocks w/ size >= msize
	''' '''
	res = []
	psls = psl_lst[:]
	for psl in psls:
		blockctr = 0
		if psl.blockCount < 2:
			continue
		for bsize in psl.blockSizes:
			if bsize >= msize:
				blockctr += 1
			if blockctr >= 2:
				res.append(psl)
				break # go to next psl
	psls = res
	#psls = psl_lst[:]
	if not psls: # if there aren't any, don't bother calling method 2
		return final_result

	# try method 2
	result = _method_2(psls, best)
	if result:
		#print "method 2 result:", result
		final_result.extend(result)
	#print final_result


	# and now look for expanded repeats
	result = _method_3(psls3, best)
	if result:
		final_result.extend(result)
		#print "final_result:", final_result

	return final_result


def _method_1(psls, best, msize=500):
	'''finds inversions'''
	#if len(psls) == 1: # why was I even doing this???
		#return [False]
	result = []
	invctr = 0
	for psl in psls:
		if "inversion" in result:
			return result
		if psl.strand != best.strand and psl != best:												# TODO: let user set "fuzz distance"
			if (abs(psl.qEnd - best.qStart) <= 50) or (abs(best.qEnd - psl.qStart) <= 50): # yup, this seems right...
				#result.append("inversion")
				invctr += 1
				'''
				print "inversion debugging:"
				print "best.matches:", best.matches
				print "psl.matches:", psl.matches
				'''
				#return "inversion"
	if invctr > 0:
		result.append("inversion|" + str(invctr))
	return result


def _method_2(psls, best):
	'''
	insertion, deletion
		gap in reference = deletion
		gap in contig	 = insertion
	'''
	psl = best
	retval = []
	delctr = 0
	insctr = 0

	if True:
		if len(psl.blockSizes) == 1:
			#continue
			#return [False]
			return []
		'''
		if _overlap(psl, best):
			continue
		'''
			# if best spans psl, ignore psl
			# should this be q or t?
			# t gets more scaffolds correct
			# q has more reporting not misassembled

		for i in xrange(1, len(psl.blockSizes)): 
			# only count blocks >= 500 bp
			# ignore blocks < 500 bp
			if psl.blockSizes[i-1] < 500 or psl.blockSizes[i] < 500:	# again with the magic number
				continue

			end_t = psl.tStarts[i-1] + psl.blockSizes[i-1]
			start_t = psl.tStarts[i]

			end_q = psl.qStarts[i-1] + psl.blockSizes[i-1]
			start_q = psl.qStarts[i]

			dist_t = abs(start_t - end_t) 
			dist_q = abs(start_q - end_q) 

			if dist_t >= 1000 and not "deletion" in retval:														# magic number, don't hardcode
				#print str("method 2: [dist_t = start - end]: "+ str(dist_t)+ " = "+ str(start_t)+ " - "+ str(end_t))
				#retval.append("deletion")
				delctr += 1
			if dist_q >= 1000 and not "insertion" in retval:														# magic number, don't hardcode
				#print str("method 2: [dist_q = start - end]: "+ str(dist_q)+ " = "+ str(start_q)+ " - "+ str(end_q))
				#retval.append("insertion")
				insctr += 1

	if delctr > 0:
		retval.append("deletion|" + str(delctr))
	if insctr > 0:
		retval.append("insertion|" + str(delctr))
	return retval


def _method_3(psls, best):
	#print "method 3..."
	possible = [best]
	#expanded_repeats = []
	expanded_repeats = set()

	# note: "psls" has already pruned alignments with < some number matches
	# minimum default number of matches == 500 bp
	for psl in psls:
		#if (psl.tStart, psl.tEnd) overlaps (best.tStart, best.tEnd):
		# should overlap on target by 1000 bp
		#if _overlap(psl, best, 1000, target=True):
		overlap, amount = _overlap(psl, best, target=True)
		#print "overlap, amount:", overlap, amount
		if best.strand == psl.strand and overlap and amount >= 1000:
			#print "appending", psl.qName
			possible.append(psl)
	
	possible_copy = possible[:]
	for pos1 in possible:
		# remove from possible_copy list current alignment we're looking at in outer loop
		possible_copy.pop(possible_copy.index(pos1))
		for pos2 in possible_copy:
			if pos1 == pos2:
				continue

			# should overlap on query but by less than 1000)
			overlap, amount = _overlap(pos1, pos2)
			#print "pos1.tStart:", pos1.tStart
			#print "pos2.tStart:", pos2.tStart
			'''
			print "query:", pos1.qName, "vs", pos2.qName
			print "overlap:", overlap, "amount:", amount
			'''
			if not (pos2, pos1) in expanded_repeats:
				if overlap and amount < 1000:
					overlap, amount = _overlap(pos1, pos2, target=True)
					if overlap and amount >= 1000:
						#expanded_repeats.extend([pos1, pos2])
						expanded_repeats.add((pos1, pos2))
	
	# give the message "expanded repeat" somehow?
	#expanded_repeats = list(set(expanded_repeats))
	'''
	print "len(expanded repeats):", len(expanded_repeats)
	print "expanded repeats:"
	for foo in expanded_repeats:
		print "tStart, tEnd:"
		print foo[0].tStart, foo[0].tEnd
		print foo[1].tStart, foo[1].tEnd
	'''
	if expanded_repeats:
		return ['expanded repeat|' + str(len(expanded_repeats))] # XXX for now, just for test
	# return expanded_repeats
	return []

def _overlap(a, b, target=False):
	'''returns true if there is overlap between the alignments'''
	# a, b are PSL entries
	#print "current contig:", a.qName

	bstart = b.qStart
	bend = b.qEnd
	astart = a.qStart
	aend = a.qEnd

	if target:
		#print "target start:", b.tStart, a.tStart
		bstart = b.tStart
		bend = b.tEnd
		astart = a.tStart
		aend = a.tEnd

	estart = 0
	eend = 0
	lstart = 0
	lend = 0

	if bstart < astart:
		#print "1 bstart:", bstart, "astart:", astart # ***
		#print "bend:", bend, "astart:", astart
		if bend <= astart and target:
			#print "returning..."
			return (False, 0)
		bend = bend - bstart
		astart = astart - bstart
		aend = aend - bstart
		bstart = 0

		estart = bstart
		eend = bend
		lstart = astart
		lend = aend

	#elif astart < bstart:
	else:
		#print "2 bstart:", bstart, "astart:", astart
		#print "aend:", aend, "bstart:", bstart
		if aend <= bstart and target:
			return (False, 0)
		aend = aend - astart
		bstart = bstart - astart
		bend = bend - astart
		astart = 0

		estart = astart
		eend = aend
		lstart = bstart
		lend = bend

	'''
	print "estart:", estart
	print "end:", eend
	print "lstart:", lstart
	print "lend:", lend
	'''
	
	overlap = False
	amount = 0

	if lstart >= estart and lstart <= eend:
		overlap = True

	if overlap:
		if lend <= eend:
			amount = lend - lstart
		else:
			amount = eend - lstart
	return (overlap, amount)
			

'''
def _overlap(a, b, overlap_dist=0, target=False):
	#returns true if there is overlap between the alignments
	# a, b are PSL entries

	bstart = b.qStart
	bend = b.qEnd
	astart = a.qStart
	aend = a.qEnd
	if target:
		bstart = b.tStart
		bend = b.tEnd
		astart = a.tStart
		aend = a.tEnd

	if a == b:
		#print a, b
		return False
	if (bstart - aend > overlap_dist) or (astart - bend > overlap_dist):
		return False
	if (bstart - aend <= overlap_dist) or (aend - bend <= overlap_dist):
		#print (bstart, bend), (astart, aend)
		return True
	if (astart - bend <= overlap_dist) or (bend - aend <= overlap_dist):
		return True
	return False
'''

def minus_strand(line):
	'''called when strand is -. "flip" bp and reverse the string; return result'''
	result = ''
	for char in line:
		if char == 'A':
			result += 'T'
		elif char == 'T':
			result += 'A'
		elif char == 'G':
			result += 'C'
		elif char == 'C':
			result += 'G'
		else:
			result += char
	return result[::-1]

def get_quast_report(quastf):
	'''return GC %, N50, N75 from Quast report'''
	def startslist(line, vals):
		for value in vals:
			if line.startswith(value):
				return True
		return False

	quastl = []
	vals = "GC N50 N75".split()
	with open(quastf, 'r') as file_:
		for line in file_:
			line = line.strip().split()
			if not line:
				continue
			if startslist(line[0], vals):
				quastl.append((" ".join(line[:-1]), line[-1]))
	return quastl


#################################################
#												#
#	Data containers (genomes, etc.)				#
#												#
#################################################

class Genome(object):
	'''base class for ReferenceGenome and ContigGenome objects'''
	def __init__(self, text):
		self.genome = ""

		wspc_rgx = re.compile(r"\s")
		nocomment_rgx = re.compile(r">*\n")

		#remove >comments, whitespace from reference genome
		# TODO: nocomment_rgx.sub(whatever), don't have to call re.foo
		self.genome = re.sub(nocomment_rgx, "", text)
		self.genome = re.sub(wspc_rgx, "", self.genome)
		self.genome = self.genome.upper()

class ReferenceGenome(Genome):
	'''Container for entire reference genome and 2 boolean lists.'''
	def __init__(self, text):
		Genome.__init__(self, text)
		self.matched = []
		self.seen = []

		# initialize matched and seen to false
		# note: don't do this with multidimensional list (1D w/tuples are OK)
		self.matched = [False] * len(self.genome)
		self.seen = [False] * len(self.genome)

class ContigGenome(Genome):
	'''container for query genome. Contig + boolean indicating misassembly'''
	def __init__(self, text):
		Genome.__init__(self, text)
		#self.misassembled = False
		self.misassembled = []

class PSLData(object):
	'''container for fields in a PSL file, ex. matches, qStarts, tBaseInsert, etc.'''

	# use slots to reduce overhead
	__slots__ = ['matches', 'misMatches', 'repMatches', 'nCount', 'qNumInsert', 'qBaseInsert',
		'tNumInsert', 'tBaseInsert', 'strand', 'qName', 'qSize', 'qStart', 'qEnd', 'tName',
		'tSize', 'tStart', 'tEnd', 'blockCount', 'blockSizes', 'qStarts', 'tStarts']
	def __init__(self, text):
		try:
			line = text.strip().split()

			self.matches = int(line[0])
			self.misMatches = int(line[1])
			self.repMatches = int(line[2])
			self.nCount = int(line[3])
			self.qNumInsert = int(line[4])
			self.qBaseInsert = int(line[5])
			self.tNumInsert = int(line[6])
			self.tBaseInsert = int(line[7])
			self.strand = line[8] # string type
			self.qName = line[9]  # string type
			self.qSize = int(line[10])
			self.qStart = int(line[11])
			self.qEnd = int(line[12])
			self.tName = line[13] # string type
			self.tSize = int(line[14])
			self.tStart = int(line[15])
			self.tEnd = int(line[16])
			self.blockCount = int(line[17])
			# Hooray, list comprehension! "if x" is required because some lists end in
			# the delimiter ','. Without "if x", there would be an entry "" in the list
			self.blockSizes = [int(x) for x in line[18].split(",") if x]
			self.qStarts = [int(x) for x in line[19].split(",") if x]
			self.tStarts = [int(x) for x in line[20].split(",") if x]
		except:
			raise Exception("Invalid line: " + text)
	
	def __iter__(self):
		for attr in dir(self):
			if not attr.startswith("__"):
				yield attr

#################################################
#												#
#	misc -- other code for various reasons		#
#												#
#################################################

# from stack overflow:
# http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
# http://stackoverflow.com/questions/8924173/python-print-bold-text

class colors:
	PURPLE = '\033[95m'
	CYAN = '\033[96m'
	DARKCYAN = '\033[36m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	END = '\033[0m'
