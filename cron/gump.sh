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
# $Header: $
ulimit -c 1
cygwin=false;
sunos=false;
case "`uname`" in
  CYGWIN*) cygwin=true ;;
  SunOS*) sunos=true ;;
esac
if $cygwin; then
   export GUMP_HOST=`hostname`
elif $sunos; then
   export GUMP_HOST=`uname -n`
else
    export GUMP_HOST=`hostname -s`
fi
export LOCAL_ENV=local-env.sh
if [ -e  $LOCAL_ENV ] ; then
	. $LOCAL_ENV
fi
export HOST_LOCAL_ENV=local-env-${GUMP_HOST}.sh
if [ -e  $HOST_LOCAL_ENV ] ; then
	. $HOST_LOCAL_ENV
fi
export HOST_LOCAL_PRE_RUN=local-pre-run-${GUMP_HOST}.sh
export HOST_LOCAL_POST_RUN=local-post-run-${GUMP_HOST}.sh

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
# Perform the run (passing on any arguments)
#
$GUMP_PYTHON gump.py $*

#
# Ensure nothing we started (directly) is left running after we end...
# :TODO: Shame we can't kill everything below us, including the indirects...
#
if [ "" != "`which pkill`" ] ; then
	pkill -KILL -P $$ 
fi

# See if this tells us much.
#times

# $Log: gump.sh,v $
