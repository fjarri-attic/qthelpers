"""
Module for application-wide convenience functions and classes.
"""

from logging import warning

from PyQt4 import QtGui, QtCore


class _GlobalsWrapper:
	"""
	Wrapper for some global variables and functions.
	This way they do not spoil the global namespace.
	"""

	@property
	def inst(self):
		"""Returns application instance"""
		return QtGui.QApplication.instance()

	@property
	def translate(self):
		"""
		Returns global application translation function.
		Using the same name in order to make lupdate happy.
		"""
		return QtGui.QApplication.translate

	@property
	def settings(self):
		"""
		Returns global application settings object.
		Creating the new one each time to avoid cases when several
		threads use the same object.
		"""
		return QtCore.QSettings()

app = _GlobalsWrapper()
