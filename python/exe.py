# exe.py
from distutils.core import setup
import py2exe

# To make a rudimentary exe dist on a wintel machine
# 1 - install py2exe [http://starship.python.net/crew/theller/py2exe/]
# 2 - run: python exedist.py py2exe

setup(name="build",
      scripts=["build.py"],
)
