#!/usr/bin/python -tt

import argparse
import sys
import subprocess
import os
import time

import src.metaMorpher_utils as mu
import src.PSLCoverage as pslc
import src.ReadBuilder as rbdr
import src.mm_configurator

def main():
	args = None
	parser = mu.get_MetaMorpher_parser()
	args = parser.parse_args()
	#print args
	#exit()

	# move all this stuff to utilities -- pretty ugly in main
	# will have to figure out how to call MetaMorpher from utils tho...
	switch = args.commands
	call = {"option" : switch}
	if switch == "SETUP": # set up config file
		mmc = src.mm_configurator.MMConfigurator()
		mmc.interactive()
		mmc.write_config()
		exit(0)

	elif switch == "RUN": # run from config file
		#call['config'] = args.config
		mmc = None
		if args.config:
			mmc = src.mm_configurator.MMConfigurator(args.config)
		else:
			mmc = src.mm_configurator.MMConfigurator()
		mmc.read_in_config()
		defaults = mmc.defaults

		args = mmc.argify()
		switch = mmc.option

	# hack because I'm lazy:
	if not hasattr(args, 'insert'):
		setattr(args, 'insert', 300)
	if switch == "noread": # user provides reads, still run assembler, blat, etc.
		call['reference'] = args.target
		call['query'] = None # create query by running assembler
		call['read1'] = args.reads
		call['read2'] = args.paired
		if args.assembler:
			call['assembler'] = args.assembler
		call['multiple'] = args.multiple
		#call['outfile'] = args.outfile # not a parser option
		call['misassembly'] = args.misassembly
		call['mismatch'] = args.mismatch
		call['quast'] = args.quast
		call['kmer'] = args.kmer
		call['blatpath'] = args.blatpath
		call['quastpath'] = args.quastpath
		call['assemblerpath'] = args.assemblerpath
		call['block'] = args.block
		call['insert_size'] = args.insert

		# MetaMorpher object drives control flow from here on.
		mmobj = MetaMorpher(**call)

	elif switch == "runall": # run everything
		# create reads
		kwargs = {"target" : args.target, "insert_size" : args.insert, 
			"error_rate" : args.error, "number_reads" : args.reads, 
			"read_size" : args.readsize, "file1" : args.file1, "file2" : args.file2,
			"seed" : args.seed, "mc" : args.multiple}
		rb = rbdr.ReadBuilder(**kwargs)
		rb.make_reads()

		# MetaMorpher object will call assembler, blat, and coverage
		call['reference'] = args.target
		call['query'] = None # created by running assembler
		call['read1'] = rb._file1 # ReadBuilder object has file names
		call['read2'] = rb._file2
		if args.assembler:
			call['assembler'] = args.assembler
		call['multiple'] = args.multiple
		call['misassembly'] = args.misassembly
		call['mismatch'] = args.mismatch
		call['quast'] = args.quast
		call['kmer'] = args.kmer
		call['blatpath'] = args.blatpath
		call['quastpath'] = args.quastpath
		call['assemblerpath'] = args.assemblerpath
		call['block'] = args.block
		call['insert_size'] = args.insert

		# MetaMorpher object drives control flow from here on.
		mmobj = MetaMorpher(**call)

	elif switch == "readsonly": # only create reads
		kwargs = {"target" : args.target, "insert_size" : args.insert, 
			"error_rate" : args.error, "number_reads" : args.reads, 
			"read_size" : args.readsize, "file1" : args.file1, "file2" : args.file2,
			"seed" : args.seed, "mc" : args.multiple, "block" : args.block}
		rb = rbdr.ReadBuilder(**kwargs)
		rb.make_reads()

	elif switch == "reportonly": #only produce report
		#kwargs = {"psl" : args.align, "contigs" : args.query, "reference" : args.target, 
			#"misassembly" : args.misassembly, "mismatch" : args.mismatch}
		#pc = pslc.PSLCoverage(**kwargs)
		#pc.fakeyreport()
		# alignment file should know if there's multiple chromosomes
		call['align'] = args.align
		call['query'] = args.query
		call['reference'] = args.target
		call['misassembly'] = args.misassembly
		call['mismatch'] = args.mismatch
		call['multiple'] = args.multiple
		call['block'] = args.block
		call['outfile'] = args.align
		call['quast'] = args.quast
		call['quastpath'] = args.quastpath
		call['insert_size'] = args.insert
		mmobj = MetaMorpher(**call)

class MetaMorpher(object):

	def __init__(self, option, reference, query, read1=None, read2=None, assembler='velvet', multiple=False, quast=False, outfile=None, misassembly=False, mismatch=False, kmer=21, assemblerpath=None, blatpath=None, quastpath=None, align=None, block=500, insert_size=300):
		self.dt = time.localtime()
		self.dt = time.strftime("%d.%m.%Y.%H.%M.%S", self.dt)
		self.topdir = assembler + self.dt + "MetaMorpher_Run"
		#self.topdir = self.dt + "MetaMorpher_Run"
		os.makedirs(self.topdir)

		self.reference = reference
		self.contigs = query # get this from assembler, check runAssembler() for more
		self.read1 = read1 # TODO: place inside topdir
		self.read2 = read2 # TODO: place inside topdir
		self.insert_size = insert_size # needed for velvet
		self.assembler = assembler
		self.mc = multiple
		self.mclist = None # populated list when multiple = True
		self.quast = quast
		if self.quast:
			self.quastdir = self.topdir + '/' + self.dt + "Quast"
			os.makedirs(self.quastdir)
		self.report_file = self.topdir + '/' + "coverage_report.txt"
		self.option = option
		self.misassembly = misassembly
		self.mismatch = mismatch

		self.blat = blatpath
		self.quastpath = quastpath
		self.assemblerpath = assemblerpath
		self._minblock = block

		if outfile or option == "reportonly":
			self.blatout = outfile
		else: 
			self.blatout = self.topdir + '/' + self.dt + ".psl"

		self.align = align # if reportonly, a hack

		# touch the psl
		print self.blatout
		if not option == 'reportonly':
			fh = open(self.blatout, "w")
			fh.close()

		# assembler options, to be set
		if kmer:
			self.kmer = kmer
		else:
			self.kmer = 21
		self.assemblerOutDir = self.topdir + '/' + self.dt + "assemblerOut"
		self.logfile = self.topdir + '/' + self.dt + ".log"
		
		self.logfile = open(self.logfile, 'w')

		self.driver()
		self.logfile.close()

	def driver(self):
		'''run assembler, blat, and PSLCoverage'''
		if not self.option == "reportonly":
			self.runAssembler()
			self.runBlat()
		else:
			self._get_chromosome_list() # called by runBlat
		self.runPSLCoverage()

	def runAssembler(self):
		# create output dir:
		if self.assembler.lower() != "ray": # Ray will complain and die if dir exists
			os.makedirs(self.assemblerOutDir)

		# call assembler 
		# get fasta file when done

		if self.assembler.lower() == "velvet":
			velPath = "" # /s/chopin/h/proj/plant_pathogen_data/owen/bioinf/velvet/"
			if self.assemblerpath:
				velPath = self.assemblerpath
			velhcmd = ""
			if self.option == "noread" :
				velhcmd = " ".join((self.assemblerOutDir, str(self.kmer), "-fasta ", self.read1))
			else:
				velhcmd = " ".join((self.assemblerOutDir, str(self.kmer), "-fasta " \
					"-separate", self.read1, self.read2))
			print "starting velveth..."
			subprocess.call(velPath +"velveth "+ velhcmd, shell=True, stdout=self.logfile)
			print "velveth done\n"

			velhcmd = velPath + "velvetg" + " " + self.assemblerOutDir + " -ins_length " + str(self.insert_size)
			print "starting velvetg..."
			subprocess.call(velhcmd, shell=True, stdout=self.logfile)
			print "velvetg done\n"

			# now set contig location!
			self.contigs = self.assemblerOutDir + "/contigs.fa"
		elif self.assembler.lower() == "spades":
			if not self.assemblerpath:
				self.assemblerpath = "spades.py" # get user feedback, does this work?
			spadescmd = self.assemblerpath + " -1 " + self.read1 + " -2 " + self.read2 + " --only-assembler -o " + self.assemblerOutDir
			print "starting spades..."
			subprocess.call(spadescmd, shell=True, stdout=self.logfile)
			print "spades done"
			self.contigs = self.assemblerOutDir + "/contigs.fasta"

		elif self.assembler.lower() == "ray":
			if not self.assemblerpath:
				self.assemblerpath = "Ray"
			raycmd = "mpiexec -n 16 " + self.assemblerpath + " -k " \
				+ str(self.kmer) + " -p " + self.read1 + " " \
				+ self.read2 + " -o " + self.assemblerOutDir
			print "starting Ray..."
			subprocess.call(raycmd, shell=True, stdout=self.logfile)
			print "Ray done"
			self.contigs = self.assemblerOutDir + "/Contigs.fasta"

		else:
			pass
			# some other assembler

	def _get_chromosome_list(self):
		thereference = ""
		files = []
		if self.mc: # multiple chromosomes
			# create new file w/one file name per line
			for file_ in os.listdir(self.reference):
				file_ = self.reference + "/" + file_
				if os.path.isdir(file_):
					continue
				files.append(file_)
			chrlist = self.topdir + '/' + self.dt + "chromosomes"
			with open(chrlist, 'w') as f:
				f.writelines(["%s\n" % line for line in files])
			thereference = chrlist
			self.mclist = files
		return thereference

	def runBlat(self):
		'''run assembler and set self.contigs'''
		# again, get config settings for Blat
		# call Blat, get output psl

		if self.blat:
			blat = self.blat + " "
		else:
			blat = 'blat '
		#blat = "/usr/local/blat/blat "
		thereference = ""
		files = []
		if self.mc: # multiple chromosomes
			thereference =  self._get_chromosome_list()
		else:
			# blat database query output.psl
			thereference = self.reference
		subprocess.call(blat  + thereference + " " + self.contigs + " " + self.blatout, \
			stdout=self.logfile, shell=True)

	def runPSLCoverage(self):
		# run PSLCoverage

		if not self.mclist:
			self.mclist = [self.reference]
		for chrom in self.mclist:
			print chrom # print out the chromosome
			p = pslc.PSLCoverage(self.blatout, self.contigs, chrom, self.misassembly,
				self.quast, self.mismatch, self._minblock)
			chrom_report = p.coverage_report(self.topdir) # print out report
			'''
			print "chrom_report:"
			print "~~~~~~~~~~~~~"
			print chrom_report
			print "~~~~~~~~~~~~~"
			'''
			#rf.write(chrom_report) # write to file

		# run Quast
		if self.quast:
			quastp = "quast" # not tested
			reference = self.reference
			if self.quastpath: # /s/oak/a/nobackup/lin/quast_eval/quast-2.2/
				quastp = self.quastpath
			if self.mc:
				reference = ','.join(self.mclist)
				quastp += 'metaquast.py'
			else:
				quastp += 'quast.py'

			call = quastp + " -o " + self.quastdir + " " + self.contigs + " -R " + reference
			subprocess.call(call, shell=True, stdout=self.logfile)

			report = self.quastdir + "/report.txt"
			if self.mc:
				report = self.quastdir + '/combined_quast_output/report.txt'
			print "todo: fix printing quast report"
			quastl = mu.get_quast_report(report)
			for item in quastl:
				print item[0] + "\t" + item[1]
			# be sure to print out self.quastdir/report.txt for GC, N50, and N75


if __name__ == '__main__':
	main()
