#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/__init__.py,v 1.20 2003/11/20 20:51:49 ajack Exp $
# $Revision: 1.20 $
# $Date: 2003/11/20 20:51:49 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2003 The Apache Software Foundation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. The end-user documentation included with the redistribution, if
#    any, must include the following acknowlegement:
#       "This product includes software developed by the
#        Apache Software Foundation (http://www.apache.org/)."
#    Alternately, this acknowlegement may appear in the software itself,
#    if and wherever such third-party acknowlegements normally appear.
#
# 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
#    Foundation" must not be used to endorse or promote products derived
#    from this software without prior written permission. For written
#    permission, please contact apache@apache.org.
#
# 5. Products derived from this software may not be called "Apache"
#    nor may "Apache" appear in their names without prior written
#    permission of the Apache Group.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.

"""
  Gump core functionality.

  It contains a sax dispatcher tool, a dependency
  walker, and an object model (GOM) which is built from an xmlfile using
  the sax dispatcher.

  The idea is that a subclass of GumpModelObject is used for each of the various
  xml tags which can appear in a gump profile, with a saxdispatcher
  generating a tree of GumpModelObject objects from the profile, dynamically
  merging as it finds href references.

  You can then use the dependencies() method to get an ordered, flat vector
  of the projects in the profile.

  Then there's some basic procedures to work with the GOM, like load().

  For basic usage patterns, look at the gump.view module or the gump.build
  module.
"""

import os.path
import os
import shutil
import string
import sys
import time

# python-2.3 or http://www.red-dove.com/python_logging.html
import logging

# base gump logger
log = logging.getLogger(__name__)

from gump.config import dir, default, setting, switch

###############################################################################
# Initialize
###############################################################################

# tell Python what modules make up the gump package
__all__ = ["config", "integrate"]

# init logging
logging.basicConfig()

#set verbosity to show all messages of severity >= default.logLevel
log.setLevel(default.logLevel)

# Ensure dirs exists,
config.basicConfig()

#
timestamp=os.path.join(dir.base,'.timestamp')
if os.path.exists(timestamp):
    default.time = os.path.getmtime(timestamp)
else:
    default.time = time.time()

default.ltime=time.localtime(default.time)
default.date = time.strftime('%Y%m%d',default.ltime)
    

###############################################################################
# Functions
###############################################################################

