import unittest
import os
import sys
sys.path.append("..")
from metaMorpher_utils import *
from PSLCoverage import PSLCoverage


class PSLCoverage_Test(PSLCoverage):
	'''dummy class for testing'''
	def __init__(self):
		'''place member variables here'''
		self._psl_file = "" # to be set
		self.psl = [] # dict holding psl objects

	def read_in_scaffold(self):
		''' 
		read psl file into memory
		Will store entire file. Use get_best_contig from metaMorpher_utils to extract
		the best alignment
		'''

		if not is_psl(self._psl_file):
			 # TODO: complain and die
			 print "not a psl: " + self._psl_file
																		     
		with open(self._psl_file, 'r') as psl_file:
			# read past comment lines...
			while not psl_file.readline().strip().startswith('-----'): 
				pass
			for line in psl_file:
				line = line.strip()
				psl = ScaffoldData(line)
				#if not psl.tName in self.refName: # psl output truncates name on whitespace
					#continue
				# self.psl[qName] = list of PSLData
				self.psl.append(psl)

class ScaffoldData(object):
	'''container for fields in a PSL file, ex. matches, qStarts, tBaseInsert, etc.'''
	def __init__(self, text):
		if True:
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
			#self.tName = line[13] # string type
			#self.tSize = int(line[14])
			self.tStart = int(line[13])
			self.tEnd = int(line[14])
			self.blockCount = int(line[15])
			# Hooray, list comprehension! "if x" is required because some lists end in
			# the delimiter ','. Without "if x", there would be an entry "" in the list
			self.blockSizes = [int(x) for x in line[16].split(",") if x]
			self.qStarts = [int(x) for x in line[17].split(",") if x]
			self.tStarts = [int(x) for x in line[18].split(",") if x]

	def __str__(self):
		#return str('[' + str(self.matches) + " " + str(self.misMatches) + " " + str(self.repMatches) + " " + str(self.nCount) + " " + str(self.qNumInsert) + " " + str(self.qBaseInsert) + " " + str(self.tNumInsert) + " " + str(self.tBaseInsert) + " " + self.strand + " " + self.qName + " " + str(self.qSize) + " " + str(self.qStart) + " " + str(self.qEnd) + ']')
		return str("[ query: start: " + str(self.qStart) + ", end: " + str(self.qEnd) + " reference: start: " + str(self.tStart) + ", end: " + str(self.tEnd) + "]")
		#return self.qName

	__repr__ = __str__
	def __repr__(self):
		foo = self.__str__()
		foo = object.__repr__(self) +'\n' + foo + '\n'
		return foo

	def __iter__(self):
		for attr in dir(self):
			if not attr.startswith("__"):
				yield attr


class TestStatics(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_is_misassembled(plist):
		'''
		need to call read_in_psl from PSLCoverage class first
		(avoid rewriting code)
		'''
		tdir = os.path.dirname(__file__) # <-- absolute dir the script is in
		def run_scaffold(scaffnum):
			pct = PSLCoverage_Test()
			scaffnum = str(scaffnum)
			rel_path = "scaffolds/scaff" +scaffnum+ ".psl"
			fpath = os.path.join(tdir, rel_path)
			pct._psl_file = fpath
			pct.read_in_scaffold()
			#print "scaffold:", scaffnum
			result = is_misassembled(pct.psl, 40)
			if not result:
				print colors.RED + colors.BOLD + "[FALSE]  " + colors.END + "scaffold "+scaffnum
			else:
				print colors.CYAN + "[OK]" + colors.END + " scaffold " + scaffnum + "\t" + str(result)
		# end _builder

		scaffolds = "0 1 3 5 6 7 11 28 34 54 81 86 94 484 1607".split()
		print "all scaffolds:", scaffolds
		for num in scaffolds:
			run_scaffold(num)
		#run_scaffold(28)
		run_scaffold(6)

		print "\n---and now expanded repeats---"
		run_scaffold("_expanded_repeats")

if __name__ == '__main__':
    unittest.main()
