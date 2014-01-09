#!/usr/bin/python2.7

import metaMorpher_utils as mmu

def misassembly(lines):
	psls = []
	for line in lines:
		pdata = mmu.PSLData(line)
		psls.append(pdata)
	result = is_misassembled(psls)
	if not result:
		print "no misassemblies detected"
	else:
		print result

def is_misassembled(psl_lst, msize=500):
	'''returns true if contig is misassembled and false otherwise'''

	# try checking length first and avoid other computations
	if len(psl_lst) == 1:
		return [False]

	psls = psl_lst[:]
	best = mmu.get_best_contig(psls)
	psls.pop(psls.index(best)) # remove "best" alignment

	# now remove elements with length < 500 bp (default msize)
	res = []
	for psl in psls:
		if psl.matches < msize:
			continue
		res.append(psl)
	else:
		psls = res

	# if there are no alignments after removing ones < 500, no misassembly
	if not psls:
		return [False]

	# now test for misassemblies (method 1)
	result =  _method_1(psls, best, msize)
	b = val = None
	if len(result) > 1:
		b, val = result
	if b:
		return val

	# put "best" alignment back in for method 2
	psls.append(best)

	# prune psls again -- remove alignments without blocks w/ size >= msize
	res = []
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
		else:
			psls = res

		if not psls: # if there aren't any, don't bother calling method 2
			return [False]

		# at last try method 2
		result  = _method_2(psls, best)
		b = val = None
		if len(result) > 1:
			print result
			b, val = result
		if b:
			return val
		return [False]


def _method_1(psls, best, msize=500):
	for psl in psls:
		if psl.strand != best.strand:
			if (psl.qEnd - best.qStart <= 100) or (best.qEnd - psl.qStart <= 100): # yup, this seems right...
				return True, "method 1"
	return [False]


def _method_2(psls, best):
	for psl in psls:
		if len(psl.blockSizes) == 1:
			continue
		for i in xrange(0, len(psl.blockSizes)): 
			end = psl.tStarts[i-1]
			start = psl.tStarts[i] + psl.blockSizes[i-1]
			dist = start - end # curr start - prev end
			if dist > 1000:
				return True, str("method 2: [dist = start - end]: "+ str(dist)+ " = "+ str(start)+ " - "+ str(end))
	return [False]
