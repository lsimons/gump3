#!/bin/bash
#
#   Copyright 2003-2004 The Apache Software Foundation
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
# $Header: $
cygwin=false;
case "`uname`" in
  CYGWIN*) cygwin=true ;;
esac
if $cygwin; then
   export GUMP_HOST=`hostname`
else
    export GUMP_HOST=`hostname -s`
fi
export LOCAL_ENV=local-env-py.sh
if [ -e  $LOCAL_ENV ] ; then
	. $LOCAL_ENV
fi
export HOST_LOCAL_ENV=local-env-py-${GUMP_HOST}.sh
if [ -e  $HOST_LOCAL_ENV ] ; then
	. $HOST_LOCAL_ENV
fi


#
# Perform the run (passing on any arguments)
#
python gumpy.py $*

#
# Ensure nothing we started (directly) is left running after we end...
# :TODO: Shame we can't kill everything below us, including the indirects...
#
if [ "" != "`which pkill`" ] ; then
	pkill -KILL -P $$ 
fi

# $Log: gumpy.sh,v $
