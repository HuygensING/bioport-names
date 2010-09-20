from setuptools import setup

setup(name = 'names',
      version = '0.2.1dev',
      packages = ['names'],
      install_requires=['python-Levenshtein',
                        'lxml',
                        'zope.component',
                        'zope.app.cache'
                       ]
      )

