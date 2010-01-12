VERSION = '0.1'

from . import build
from .build import QtProject
from .application import Application, fillSettings
from .globals import app
from . import log
from .i18n import dynamically_translated, TranslationsList

def importResources():
	__import__(build.pyResourceFileName())
