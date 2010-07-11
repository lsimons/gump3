#!/bin/bash
#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# This script will self-test Gump (Python) Capabilities
#
#
# $Header$

export

#
# Determine the Python to use... (if not told)
# 
if [ "" == "$GUMP_PYTHON" ] ; then
  export GUMP_PYTHON="`which python2.3`"
  if [ "" == "$GUMP_PYTHON" ] ; then
    export GUMP_PYTHON="`which python`"
	if [ "" == "$GUMP_PYTHON" ] ; then
	  echo "No Python (python2.3 nor python) found in path."
	  exit 1
	fi
  fi
fi

#
# Perform some Gump unit test
#
cd python

echo "--------------------------------------------------"
echo "Run ... $GUMP_PYTHON gump/test/pyunit.py"
$GUMP_PYTHON gump/test/pyunit.py

#echo "--------------------------------------------------"
#echo "Run the environment check"
#$GUMP_PYTHON ../bin/env.py


#echo "--------------------------------------------------"
# echo "Run the Workspace check"
# $GUMP_PYTHON ../bin/check.py -w ../metadata/test-workspace.xml all --debug


#echo "--------------------------------------------------"
# echo "Run the Workspace preview"
# $GUMP_PYTHON ../bin/preview.py -w ../metadata/test-workspace.xml all --debug
