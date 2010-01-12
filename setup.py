import sys
major, minor, micro, releaselevel, serial = sys.version_info

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from qthelpers import VERSION

setup(
	packages=['qthelpers'],
	version=VERSION,
	author='Bogdan Opanchuk',
	author_email='bg@bk.ru',
	url='http://github.com/Manticore/qthelpers',
	description='Helper library for PyQt',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Topic :: Software Development :: Libraries :: Python Modules',
	]
)
