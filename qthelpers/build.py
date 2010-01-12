"""
Object, encapsulating build procedures for PyQt project
"""

from PyQt4 import QtCore

import os
import os.path
import shutil
import sys
from subprocess import Popen

from . import i18n

def _execute(cmd):
	result = Popen(cmd).wait()
	if result != 0:
		raise Exception("Error: " + str(result))

def _fileListVariable(name, values):
	return name + " = \\\n\t" + " \\\n\t".join(values) + "\n"

_PROJECT_FILE = "project.pro"
_RESOURCE_FILE = "resources.qrc"

def pyResourceFileName():
	return "resources_qrc"

class QtProject:

	def __init__(self, app_dir, sources=None, default_locale=None):
		self._app_dir = app_dir
		self._sources = sources
		self._default_locale = default_locale

	def _createProjectFile(self, sources, translations):
		contents = _fileListVariable("SOURCES", sources) + "\n" + \
			_fileListVariable("RESOURCES", [_RESOURCE_FILE]) + "\n" + \
			_fileListVariable("TRANSLATIONS",
				[x + ".ts" for x in translations]) + "\n"

		project = open(_PROJECT_FILE, 'w')
		project.write(contents)
		project.close()

	def _createResourceFile(self, translations):
		contents = "<!DOCTYPE RCC><RCC version=\"1.0\">\n<qresource>\n" + \
			"\n".join(["<file>" + x + ".qm</file>" for x in translations]) + \
			"\n</qresource>\n</RCC>\n"

		qrc = open(_RESOURCE_FILE, 'w')
		qrc.write(contents)
		qrc.close()

	def _getSourcesList(self):
		"""
		Generate list of sources for project file. If list was specified 
		explicitly during object creation, it is returned, otherwise
		list of all .py files in app directory is returned.  
		"""
		if self._sources is not None:
			return self._sources

		sources = []
		files = os.listdir(self._app_dir)
		for file in files:
			name, ext = os.path.splitext(file)
			if ext == ".py":
				sources.append(file)
		return sources

	def _buildResources(self):
		os.chdir(self._app_dir)
		_execute(["pylupdate4", _PROJECT_FILE])
		_execute(["lrelease", _PROJECT_FILE])

		major, minor, micro, releaselevel, serial = sys.version_info
		_execute(["pyrcc4", _RESOURCE_FILE, "-o", pyResourceFileName() + ".py"] +
			(["-py3"] if major == 3 else []))

	def build(self):
		sources = self._getSourcesList()
		translations = i18n.findTranslationFiles(self._app_dir)

		if self._default_locale is not None:
			locale = QtCore.QLocale(self._default_locale)
			file_name = i18n.getTranslationFileName(locale)
			if file_name in translations:
				src = os.path.join(self._app_dir, file_name + ".ts")
				dst_name = i18n.getTranslationFileName()
				shutil.copyfile(src, dst_name + ".ts")
				translations.append(dst_name)

		self._createProjectFile(sources, translations)
		self._createResourceFile(translations)
		self._buildResources()
