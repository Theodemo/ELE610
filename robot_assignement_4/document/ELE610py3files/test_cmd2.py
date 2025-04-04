#!/usr/bin/env python
"""A simple cmd2 application. From https://cmd2.readthedocs.io/en/stable/examples/first_app.html#first-application
and added more as I followed the instructions
"""

import cmd2
import argparse


class FirstApp(cmd2.Cmd):
	"""A simple cmd2 application."""

	def __init__(self):
		super().__init__()

		# Make maxrepeats settable at runtime
		self.maxRepeats = 3
		self.add_settable(cmd2.Settable('maxRepeats', int, 'Max repetitions for speak command', self))


	speak_parser = cmd2.Cmd2ArgumentParser()
	speak_parser.add_argument('-p', '--piglatin', action='store_true', help='atinLay')
	speak_parser.add_argument('-s', '--shout', action='store_true', help='N00B EMULATION MODE')
	speak_parser.add_argument('-r', '--repeat', type=int, help='output [n] times')
	speak_parser.add_argument('words', nargs='+', help='words to say')
	@cmd2.with_argparser(speak_parser)
	def do_speak(self, args):
		"""Repeats what you tell me to."""
		words = []
		for word in args.words:
			if args.piglatin:
				word = '%s%say' % (word[1:], word[0])
			if args.shout:
				word = word.upper()
			words.append(word)
		repetitions = args.repeat or 1
		for _ in range(min(repetitions, self.maxRepeats)):
			# .poutput handles newlines, and accommodates output redirection too
			self.poutput(' '.join(words))


if __name__ == '__main__':
	import sys
	c = FirstApp()
	sys.exit(c.cmdloop())
