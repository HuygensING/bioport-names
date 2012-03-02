from setuptools import setup

setup(name = 'names',
      version = '0.3.2',
      packages = ['names'],
      install_requires=['python-Levenshtein',
                        'lxml',
                        'zope.component',
#                        'zope.app.cache==3.4'
                        'zope.app.cache',
                       ]
      )

