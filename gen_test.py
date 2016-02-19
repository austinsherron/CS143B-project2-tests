#!/usr/bin/python

import sys

from collections import defaultdict
from random import randint
from random import random
from random import sample
from string import ascii_lowercase as abc


class GenTest:

	def __init__(self, num_files, length, err, commands=None):
		self.num_files = num_files 		# number of files
		self.length = length			# number of commands
		self.err = err					# probability of explicity errors
		# set of all files
		self.files = set([abc[i] for i in range(num_files)])
		# map of commands to probabilities of occurence
		self.commands = {'op', 'cl', 'sk', 'rd', 'wr', 'cr', 'de', 'dr'}
		self.commands = commands if commands else dict([(c,0.2) for c in self.commands])
		self.open = set() 				# set of open files
		self.created = set()			# set of existent files
		self.max_open = 3				# max number of open files
		self.OFT = [None] * 4			# OFT (need to keep tack of indices)


	def gen_op(self):
		# can't open if no files exist
		if len(self.created) == 0:
			return

		# errs
		if random() <= self.err:
			t = random()
			# open when OFT is full
			if t < 0.5 and len(self.open) == self.max_open:
				return 'op {}'.format(sample(self.files - self.open, 1)[0])
			# open a file that doesn't exist; foo will never be created
			elif t < 0.5:			
				return 'op foo'
			# open a file that's already open
			elif len(self.open) > 0:				
				return 'op ' + sample(self.open, 1)[0]

		# valid
		elif len(self.open) < self.max_open and len(self.created - self.open) > 0:
			# choose non open file
			file = str(sample(self.created - self.open, 1)[0])
			# add file to open set
			self.open.add(file)
			# add file to OFT
			self._OFT_insert(file)
			return 'op ' + file


	def gen_cl(self):
		# errs
		if random() <= self.err:
			# close random OFT index; might not be an error if OFT is full
			index = self._bad_file_index()
			return 'cl {}'.format(index)

		# valid
		elif len(self.open) > 0:
			# find valid OFT index
			closing = self._file_index()
			# delete from open files
			self.open.remove(self.OFT[closing])
			# delete from OFT
			self.OFT[closing] = None
			return 'cl {}'.format(closing)


	def gen_sk(self):
		# errs 
		if random() <= self.err:
			# seek on empty OFT index; might not be error if OFT is full
			pool = [i for i in range(len(self.OFT)) if self.OFT[i] is None and i != 0]
			index = sample(pool, 1)[0] if len(pool) > 0 else randint(1, 4)
			return 'sk {} {}'.format(index, randint(0, 192))

		elif len(self.open) > 0:
			# seek to a random position; may be an invalid seek
			return 'sk {} {}'.format(self._file_index(), randint(0, 200))


	def gen_rd(self):
		# errs 
		if random() <= self.err:
			# read on empty OFT index; might not be error if OFT is full
			pool = [i for i in range(len(self.OFT)) if self.OFT[i] is None and i != 0]
			index = sample(pool, 1)[0] if len(pool) > 0 else randint(1, 4)
			return 'rd {} {}'.format(index, randint(0, 192))

		# read a random number of bits; may be an invalid read
		elif len(self.open) > 0:
			return 'rd {} {}'.format(self._file_index(), randint(0, 200))


	def gen_wr(self):
		char = sample(abc, 1)[0]

		# errs 
		if random() <= self.err:
			# write on empty OFT index; might not be error if OFT is full
			pool = [i for i in range(len(self.OFT)) if self.OFT[i] is None and i != 0]
			index = sample(pool, 1)[0] if len(pool) > 0 else randint(1, 4)
			return 'wr {} {} {}'.format(index, char, randint(0, 192))

		# write a random number of bits; may be an invalid write
		elif len(self.open) > 0:
			return 'wr {} {} {}'.format(self._file_index(), char, randint(0, 200))


	def gen_cr(self):
		# errs
		if random() <= self.err and len(self.created) > 0:
			# cr file that exists
			file = sample(self.created, 1)[0]
			return 'cr {}'.format(file)

		# cr valid file
		elif len(self.created) < 25:
			file = sample(self.files - self.created, 1)[0]
			self.created.add(file)
			return 'cr {}'.format(file)

	
	def gen_de(self):
		# delete file that doesn't exist
		if random() < self.err and len(self.created) < 25:
			file = sample(self.files - self.created, 1)[0]
			return 'de {}'.format(file)
		# delete file that exists, if there are any
		elif len(self.created) > 0:
			file = sample(self.created, 1)[0]
			if file in self.open:
				self.OFT[self.OFT.index(file)] = None
				self.open.remove(file)
			self.created.remove(file)
			return 'de {}'.format(file)


	def gen_dr(self):
		return 'dr'


	def select_with_prob(self, frm):
		select_from = []
		for k,v in frm.items():
			select_from += [k] * int(v * 100)
		return sample(select_from, 1)[0]


	def gen(self, in_file=None):
		out = []

		while len(out) < self.length:
			command = self.select_with_prob(self.commands)
			func = 'self.gen_' + command + '()'
			command = eval('self.gen_' + command + '()')
			
			if command:
				out.append(command)

		init = 'in{}'.format(in_file if in_file else '')
		print(init)
		for command in out:
			print(command)
		print('sv dump')


	def _OFT_insert(self, file):
		for i in range(len(self.OFT)):
			if i != 0 and self.OFT[i] == None:
				self.OFT[i] = file
				return i

		return -1


	def _file_index(self):
		pool = [i for i in range(len(self.OFT)) if self.OFT[i] is not None]
		return sample(pool, 1)[0]


	def _bad_file_index(self):
		pool = [i for i in range(len(self.OFT)) if self.OFT[i] is None and i != 0]
		index = sample(pool, 1)[0] if len(pool) > 0 else randint(1, 4)
		return index
		
	
if __name__ == '__main__':

	num_files,length = 5,20
	if len(sys.argv) > 1:
		num_files = int(sys.argv[1])

	if len(sys.argv) > 2:
		length = int(sys.argv[2])

	# command probs
	commands = ['op', 'cl', 'sk', 'rd', 'wr', 'cr', 'de', 'dr']
	probs	 = [ .15,   .1,  .00,  .25,  .20,  .20,  .05,  .05]
	commands = dict(zip(commands, probs))
	
	# explicit error probs
	err = 0.05

	gt = GenTest(num_files, length, err, commands=commands)
	gt.gen()
