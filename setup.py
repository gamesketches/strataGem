from distutils.core import setup
import py2exe, sys, os

setup(console=["main.py"],
      options = {"py2exe":{"compressed":1,
                           "optimize": 2,
                           "ascii": 1,
                           "packages": []}}, zipfile = None, )
