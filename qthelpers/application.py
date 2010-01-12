"""
Main application class.
"""

from logging import warning, error

from PyQt4 import QtGui, QtCore

from .globals import app
from . import i18n


def fillSettings(data):
	"""Fill missing settings with default ones"""

	def fill(settings, dict_obj):
		for key in dict_obj:
			if isinstance(dict_obj[key], dict):
				settings.beginGroup(key)
				fill(settings, dict_obj[key])
				settings.endGroup()
			else:
				if not settings.contains(key):
					settings.setValue(key, dict_obj[key])

	settings = QtCore.QSettings()
	fill(settings, data)

class Application(QtGui.QApplication):

	def __init__(self, argv, app_name, organization_name=None):

		QtGui.QApplication.__init__(self, argv)
		self.setApplicationName(app_name)
		if organization_name is not None:
			self.setOrganizationName(organization_name)

		i18n.ensureLanguageSetting()

		self.__translator = None
		self.__reloadTranslator()

	def __reloadTranslator(self):
		"""
		Reload translator file according to current language
		value from settings.
		"""
		translator = QtCore.QTranslator()

		# get current language; if it is None, use current locale

		lang_from_config = i18n.getCurrentLanguage()
		if lang_from_config is None:
			locale = QtCore.QLocale.system()

			# load most suitable translation
			if not translator.load(i18n.getTranslationFileName(locale), ":/"):
				error("Failed to find suitable translation file for current locale ("
					+ locale.name() + ")")
		else:
			translations = {}
			for locale_name, _, full_path in i18n.findTranslationResources():
				translations[locale_name] = full_path

			# load translation file
			if lang_from_config in translations:
				if not translator.load(translations[lang_from_config]):
					error("Failed to load translation file " +
						translations[lang_from_config])
					return
			else:
				error("Translation file for " +
					lang_from_config + " was not found")
				return

		# remove old translator and install the newly loaded one

		if self.__translator is not None:
			self.removeTranslator(self.__translator)
			self.__translator = None

		self.installTranslator(translator)
		self.__translator = translator

	def event(self, e):
		if e.type() == QtCore.QEvent.LocaleChange:
			self.__reloadTranslator()

		return QtGui.QApplication.event(self, e)
