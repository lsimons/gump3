#!/usr/bin/python

# Copyright 2003-2004 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


#
# $Header: /home/stefano/cvs/gump/python/exe.py,v 1.3 2004/04/06 15:57:11 ajack Exp $
# 

# exe.py
from distutils.core import setup
import py2exe

# To make a rudimentary exe dist on a wintel machine
# 1 - install py2exe [http://starship.python.net/crew/theller/py2exe/]
# 2 - run: python exedist.py py2exe

setup(name="integrate",scripts=["integrate.py"],)
