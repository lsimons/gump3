#!/bin/bash
#
#   Copyright 2001-2004 The Apache Software Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# This script will self-test Gump (Python) Capabilities
#
#
# $Header$

export

#
# Determine the Python to use...
# 
export GUMP_PYTHON="`which python2.3`"
if [ "" == "$GUMP_PYTHON" ] ; then
 export GUMP_PYTHON="`which python`"
 if [ "" == "$GUMP_PYTHON" ] ; then
 	echo "No Python (python2.3 nor python) found in path."
 	exit 1
 fi
fi

#
# Perform some Gumpy unit test
#
cd python
$GUMP_PYTHON gump/test/pyunit.py