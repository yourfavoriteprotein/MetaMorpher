#!/usr/bin/python2.7 -tt
import os
import sys

'''
Input:  -fastq

Output: -fasta
'''

def main():
	# get the fastq file:
	# .fq or .fastq

	if len(sys.argv) != 2 or sys.argv[1].lower() in ['-h', '-help']:
		print "input: fastq output: fasta"
		print "Usage:", sys.argv[0], "<file.fastq>"
		exit(0)
	
	convert(sys.argv[1])

def convert(filenm):
	fasta = filenm[:len(filenm) - 1 - filenm[::-1].index('.')]
	fasta += ".fasta"
	output = open(fasta, 'w') # new file handle, remember to close it

	with open(filenm, 'r') as fastq:
		nextline = False
		for line in fastq:
			contents = line.strip()
			if contents.startswith('@'):
				nextline = True
				name = '>' + contents[1:] + '\n'
				output.write(name)
			elif nextline:
				nextline = False
				contents += '\n'
				output.write(contents)

	output.close()
			

if __name__ == '__main__':
    main()
