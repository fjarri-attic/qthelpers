from logging import info, warning
import os
import os.path

from PyQt4 import QtCore, QtGui

from .globals import app

_TS_NAME_BASE = "translation"
_QT_UNKNOWN_LOCALE = "C"

# user interface language (in form of locale name); None = try to find the most 
# suitable translation for current locale
_LANGUAGE_SETTING = 'i18n/language'

class _DynamicTranslator:
	"""Wrapper for dynamically translated strings"""

	class Changer:
		"""Class which wraps a single dynamically translated string"""

		def __init__(self, changer_func):
			self._changer_func = changer_func
			self._text = None

		def translate(self, context, text):
			"""
			Remember translation identifiers.
			Using this name so that it is parsed by lupdate.
			"""
			self._context = context
			self._text = text

			# Since it is used instead of actually translating something,
			# we need to pass initial translation to changer function.
			self.refresh()

		def refresh(self):
			if self._text is None:
			# Custom string builder (has translation functions inside)
				self._changer_func()
			else:
			# Just set translated string
				self._changer_func(app.translate(self._context, self._text))

	def __init__(self):
		self._changers = []

	def add(self, changer_func):
		"""Register function, which takes new translation as an argument"""
		c = self.Changer(changer_func)
		self._changers.append(c)
		return c

	def refresh(self):
		"""Refresh all translations and pass them to corresponding changer functions"""
		for changer in self._changers:
			changer.refresh()


def dynamically_translated(qwidget_class):
	"""
	Decorator which adds dynamic translation ability to class.
	Class should be a ancestor of QWidget (because it introduces
	changeEvent() method).
	"""

	class DynTrClass(qwidget_class):
		"""Wrapper for given class with dynamic translation mix-in"""

		def __init__(self, *args, **kwds):
			self.__dyntr = _DynamicTranslator()
			qwidget_class.__init__(self, *args, **kwds)

		def dynTr(self, changer_func):
			"""
			Register dynamical translation; returns Changer object
			(for which either translate() or refresh() should be called
			to set the initial translation)
			"""
			return self.__dyntr.add(changer_func)

		def changeEvent(self, e):
			"""React on language change event - refresh all translations"""
			if e.type() == QtCore.QEvent.LanguageChange:
				self.__dyntr.refresh()
			qwidget_class.changeEvent(self, e)

	# Preserve initial name of the class, to help in debugging
	DynTrClass.__name__ = qwidget_class.__name__
	return DynTrClass


def setLanguage(locale_name):
	app.settings.setValue(_LANGUAGE_SETTING, locale_name)
	event = QtCore.QEvent(QtCore.QEvent.LocaleChange)
	app.inst.postEvent(app.inst, event)

def getCurrentLanguage():
	return app.settings.value(_LANGUAGE_SETTING)

def ensureLanguageSetting():
	if not app.settings.contains(_LANGUAGE_SETTING):
		setLanguage(None)

def _parseTranslationFileName(file_name, filter_ext=None):

	# separate extension
	name, ext = os.path.splitext(file_name)
	if filter_ext is not None and ext != "." + filter_ext:
		raise Exception("Wrong file extension")

	# separate locale name
	name, locale_suffix = os.path.splitext(name)

	if name != _TS_NAME_BASE:
		raise Exception("Wrong translation name base")

	if len(locale_suffix) == 0:
	# default translation
		return QtCore.QLocale(_QT_UNKNOWN_LOCALE)

	if len(locale_suffix) == 3:
	# only language is specified
		locale_name = locale_suffix[1:] # remove leading dot
	elif len(locale_suffix) == 6:
	# language and country are specified
		# '.en_us' -> 'en_US'
		locale_suffix = locale_suffix[1:]
		locale_name = locale_suffix[:3] + locale_suffix[3:].upper()
	else:
		raise Exception("Wrong locale name format")

	locale = QtCore.QLocale(locale_name)
	if locale.name() == _QT_UNKNOWN_LOCALE:
		raise Exception("Wrong locale name")

	return locale

def _getLocaleInfo(locale):
	locale_name = locale.name()
	if locale_name != _QT_UNKNOWN_LOCALE:
		country_name = QtCore.QLocale.countryToString(locale.country())
		language_name = QtCore.QLocale.languageToString(locale.language())
		full_name = language_name + " (" + country_name + ")"
	else:
		full_name = None

	return locale_name, full_name

def getTranslationFileName(locale, ext=None):
	locale_name, _ = _getLocaleInfo(locale)
	return _TS_NAME_BASE + "." + locale_name.lower() + ('.' + ext if ext is not None else '')

def findTranslationFiles(app_dir):
	info("Looking for translation files...")

	files = os.listdir(app_dir)
	found = []

	# searching for files with names 'app_name.locale.ts'
	for file in files:
		try:
			locale = _parseTranslationFileName(file, filter_ext="ts")
		except:
			continue

		found.append(locale)

	if len(found) == 0:
		warning("No translations found.")

	return [_getTranslationFileName(locale) for locale in found]

def findTranslationResources():
	"""
	Find all valid translation files in resources and return list of tuples
	(locale name, full language name, path to file in Qt resources).
	"""

	translations_dir = QtCore.QDir(':/')
	file_names = translations_dir.entryList(['*.qm'],
		QtCore.QDir.Files, QtCore.QDir.Name)

	translator = QtCore.QTranslator()

	translation_files = []
	for file_name in file_names:
		resource_path = translations_dir.filePath(file_name)

		try:
			locale = _parseTranslationFileName(file_name)
		except:
			# theoretically, this should not happen, because these files 
			# have already passed through findTranslationFiles()
			warning("Failed to parse translation file name: " + file_name)

		if not translator.load(resource_path):
			warning("Failed to load translation file " + resource_path)
			continue

		locale_name, full_name = _getLocaleInfo(locale)

		# do not include default locale to list, we do not want to show it to user
		# it will be used only as a backup one
		if locale_name == _QT_UNKNOWN_LOCALE:
			continue

		translation_files.append((locale_name, full_name, resource_path))

	return translation_files


@dynamically_translated
class TranslationsList(QtGui.QComboBox):

	def __init__(self, parent=None, translate_current_locale=None):
		QtGui.QComboBox.__init__(self, parent)
		self._translate_current_locale = translate_current_locale

		translation_files = findTranslationResources()
		lang_from_config = getCurrentLanguage()

		# predefined entry for current locale
		languages = [(None, '')]
		for locale_name, full_name, _ in translation_files:
			# do not show default translation to user
			if locale_name != _QT_UNKNOWN_LOCALE:
				languages.append((locale_name, full_name))

		for i, e in enumerate(languages):
			locale_name, full_name = e

			self.insertItem(i, full_name, locale_name)
			if locale_name == lang_from_config:
				self.setCurrentIndex(i)

		self.currentIndexChanged.connect(self._languageChanged)
		self.dynTr(self._retranslate).refresh()

	def _retranslate(self):
		self.setItemText(0, self._translate_current_locale())

	@QtCore.pyqtSlot(int)
	def _languageChanged(self, index):
		locale_name = self.itemData(index)
		setLanguage(locale_name)
