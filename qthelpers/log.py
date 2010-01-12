"""
Module with helper functions for logging handlers initialization
"""

import logging

from PyQt4 import QtCore

_QT_LOGGER = logging.getLogger("Qt")

# mapping Qt log messages to Python handlers
_QT_LOG_HANDLERS = {
	QtCore.QtDebugMsg: _QT_LOGGER.debug,
	QtCore.QtWarningMsg: _QT_LOGGER.warning,
	QtCore.QtCriticalMsg: _QT_LOGGER.error,
	QtCore.QtFatalMsg: _QT_LOGGER.critical
}

def _qtLogToPythonLog(message_type, message):
	"""Handler for Qt log messages"""
	if isinstance(message, bytes):
		message = message.decode()
	_QT_LOG_HANDLERS[message_type](message)

def init():
	"""Initialize application log handlers"""

	# root logger
	main_handler = logging.StreamHandler()
	main_formatter = logging.Formatter("%(module)s (%(lineno)d) [%(levelname)s] %(message)s")
	main_handler.setFormatter(main_formatter)
	logging.getLogger().addHandler(main_handler)

	# special handler for Qt messages
	# we cannot get module/line number/etc for them, so using different formatter
	qt_handler = logging.StreamHandler()
	qt_formatter = logging.Formatter("Qt [%(levelname)s] %(message)s")
	qt_handler.setFormatter(qt_formatter)
	_QT_LOGGER.propagate = False
	_QT_LOGGER.addHandler(qt_handler)

	QtCore.qInstallMsgHandler(_qtLogToPythonLog)
