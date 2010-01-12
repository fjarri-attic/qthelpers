VERSION = '0.1'

from .build import QtProject
from .application import Application, fillSettings
from .globals import app
from .log import init as initLog
from .i18n import dynamically_translated, TranslationsList

def importResources():
	__import__(build.pyResourceFileName())
