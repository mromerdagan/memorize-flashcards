#!/usr/bin/python
import subprocess
import re
import random

class CardException(Exception):
	pass

class EmptyCardException(CardException):
	pass

class Card(object):
	def __init__(self, hash_, path, lesson, period):
		self.hash_ = hash_
		self.path = path
		try:
			self.lesson = int(lesson)
		except ValueError:
			if (lesson == '-'):
				self.lesson = None
			else:
				raise
		try:
			self.period = int(period)
		except ValueError:
			if (period == '-'):
				self.period = None
			else:
				raise
		self.content = self._parse_content()

	def __repr__(self):
		return "Card({}, {}, {}, {})".format(\
			self.hash_, \
			self.path, \
			self.lesson if self.lesson else '-', \
			self.period if self.period else '-', \
			)

	def _get_raw_content(self):
		cmd = 'memorize-flashcards-course show-card {}'.format(self.hash_)
		try:
			output = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		except Exception, e:
			print "E: Failed running command: {}. Got exception: {}".format(cmd, e)
			raise
		out, _ = output.communicate()
		return out

	@staticmethod
	def _is_header_line(line):
		pat = r'\S+:.*'
		m = re.match(pat, line)
		return (m != None)

	def _parse_content(self):
		ret = {}
		content = self._get_raw_content()
		content = content.split("\n")
		content = filter(bool, content) # Remove possible empty lines
		# Sanity: make sure line starts with header
		if not(content):
			raise EmptyCardException("Card empty? ({})".format(self.path))
		# Sanity: make sure line starts with header
		if not(self._is_header_line(content[0])):
			raise Exception("Card content looks bad ({})".format(self.path))

		## Split into headers groups
		content_groups = []
		while content:
			header_group = []
			header = content.pop(0)
			header_group.append(header)
			while (content and not(self._is_header_line(content[0]))):
				header_group.append(content.pop(0))
			content_groups.append(header_group)

		for group in content_groups:
			pat = r'(\S+):(.*)'
			first_line = group[0]
			m = re.match(pat, first_line)
			if not(m):
				raise Exception("Failed parsing card line: '{}' (card hash: {})".format(first_line, self.hash_))
			header = m.group(1)
			first_line = first_line[len(header)+2:]
			group[0] = first_line
			ret[header] = "\n".join(group)
		return ret

	def get_key_val(self, key):
		if not(key in self.content):
			raise Exception("Key '{}' is missing from card content".format(key))
		return self.content[key]


class Policy(object):
	def __init__(self, coursename):
		self.coursename = coursename
		self._verify_course()
		self.cards = self._read_cards()

	def _verify_course(self):
		cmd = 'memorize-flashcards-course list'
		try:
			output = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		except Exception, e:
			print "E: Failed running command: {}. Got exception: {}".format(cmd, e)
			raise
		out, _ = output.communicate()
		courses = out.split('\n')
		courses = [course.strip() for course in courses]
		courses = filter(bool, courses)
		if not(self.coursename in courses):
			raise Exception('E: Course "{}" is missing from courses db (available courses: {})'.format(\
				self.coursename, \
				" ,".join(['"{}"'.format(c) for c in courses]) \
				))

	def _read_cards(self):
		# output = subprocess.Popen('memorize-flashcards-course list'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		cmd = 'memorize-flashcards-course show-course {}'.format(self.coursename)
		try:
			output = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		except Exception, e:
			print "E: Failed running command: {}. Got exception: {}".format(cmd, e)
			raise
		out, _ = output.communicate()
		out = out.split('\n')
		out = map(lambda s: s.strip(), out)
		out = map(lambda s: s[:s.find('#')] if '#' in s else s, out)
		out = filter(bool, out)
		out = [Card(*line.split()) for line in out]
		return out

	@staticmethod
	def sorting_key(card):
		return card.lesson if card.lesson else float('inf')

	## Public methods
	def write_changes(self):
		for card in self.cards:
			if (card.lesson == None):
				continue
			cmd = 'memorize-flashcards-course update-card {} {} {} {}'.format(\
				self.coursename, \
				card.hash_, \
				card.lesson, \
				card.period, \
				)
			try:
				output = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			except Exception, e:
				print "E: Failed running command: {}. Got exception: {}".format(cmd, e)
				raise
			_, _ = output.communicate()

	def sort_cards(self):
		self.cards.sort(key=self.sorting_key)

	def course_table_str(self):
		ret = ''
		fomatter = "{:<35} {:<74} {:<7} {}"
		ret += fomatter.format('# Hash', 'Path', 'Lesson', 'Period') + "\n"
		for card in sorted(self.cards, key=self.sorting_key):
			ret += fomatter.format(card.hash_, \
				card.path, card.lesson if card.lesson else '-', \
				card.period if card.period else '-') + \
				"\n"
		ret.strip()
		return ret

	# Abstract methods
	def fetch_card(self):
		raise NotImplementedError('Abstract method. Implemented in sub classes')

	def update_card(self, card, value):
		raise NotImplementedError('Abstract method. Implemented in sub classes')

class ClassicPolicy(Policy):
	def __init__(self, coursename):
		Policy.__init__(self, coursename)
		self.LESSON_MIN_LENGTH = 5
		self.sort_cards()
		self.used_pile = [] # Will hold cards that were seen in current session

	## Helpers
	def _get_lesson(self, index):
		return [card for card in self.cards if card.lesson == index]

	def _fresh_cards(self):
		return self._get_lesson(None)

	def _fill_course(self, index):
		while (len(self._get_lesson(index)) < self.LESSON_MIN_LENGTH):
			try:
				freshcard = random.choice(self._fresh_cards())
			except IndexError:
				break
			freshcard.lesson = index
			freshcard.period = 1

	def _standardize_lessons(self):
		min_lesson = min([card.lesson for card in self.cards if card.lesson])
		diff = min_lesson - 1
		if diff:
			for card in self.cards:
				if (card.lesson != None):
					card.lesson -= diff

	def _fix_first_lesson(self):
		if (len(self.cards) == 0):
			self.cards = self.used_pile
			self.used_pile = []
		self.sort_cards()
		if self.cards[0].lesson == 1:
			return
		self._fill_course(2)
		self._standardize_lessons()

	## Public methods, derived from super class
	def fetch_card(self):
		self._fix_first_lesson()
		card = self.cards.pop(0)
		return card

	def update_card(self, card, value):
		if (card in self.cards) or (card in self.used_pile):
			raise Exception("Illegal state- card must be out of pile and used pile when updated")
		#print "D: card lesson before: {}".format(card.lesson)
		if (value == True):
			card.lesson += card.period
			card.period *= 2
		else: # value == False
			card.lesson += 1
			card.period = 1
		self.used_pile.append(card)
		#print "D: card lesson after: {}".format(card.lesson)
	
	def write_changes(self): # Override write_changes so I can combine self.cards and self.used_pile before writing
		self.cards += self.used_pile
		self.used_pile = []
		#super(ClassicPolicy, self).write_changes()
		Policy.write_changes(self)

#if __name__ == "__main__":
#	p = ClassicPolicy('perl-lamma')
#	#print "\n".join([c.__repr__() for c in p.cards])
#	#print p.course_table_str()
#	while True:
#		c = p.fetch_card()
#		print c.content
#		p.update_card(c, True)
#		raw_input()

