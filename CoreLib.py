from abc import ABC,abstractmethod
import math
import re

class CoreLib():
	
	@staticmethod
	def merge_two_dicts(x, y):
		"""Given two dicts, merge them into a new dict as a shallow copy."""
		z = x.copy()
		z.update(y)
		return z
		
	@staticmethod
	def padLine(line):
		"""Pads a line out to fit on the screen"""
		linediff = math.floor((20 - len(line))/2)
		return (" "*linediff)+line

	@staticmethod
	def stripEmail(username):
		email_regex = re.compile('(^.*)@.*',re.IGNORECASE)
		if "@" in username:
			return email_regex.match(username).group(1)
		else:
			return username

class DataSource(ABC):
	
	@abstractmethod
	def getData(self): raise NotImplementedError


class DataNotThereError(Exception):
	def __init__(self, message, errors):

		# Call the base class constructor with the parameters it needs
		super().__init__(message)