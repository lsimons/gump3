#!/bin/bash
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
if [ ! $GUMP ] ; then
	echo "Set the \$GUMP variable to your gump install (e.g. /opt/jakarta-gump)"
	exit 1
fi

if [ ! $GUMP_WS ] ; then
	echo "Set the \$GUMP_WS variable to your gump working area (e.g. /var/gump)"
	exit 1
fi

if [ ! $GUMP_LOG_DIR ] ; then
	echo "Set the \$GUMP_LOG_DIR variable to your gump WWW diredtory (e.g. /var/www/html/gump)"
	exit 1
fi

if [ -n "$1" ] ; then
	export GUMP_TARGET=$1
else
	export GUMP_TARGET=all
fi

#
# Calculated
#
export GUMPY_VERSION="1.0.6"
export GUMP_PYTHON=$GUMP/python
export GUMP_TMP=$GUMP/tmp
export GUMP_WS_TMP=$GUMP_WS/tmp
export GUMP_DATE=`date`
export GUMP_LOG=$GUMP_LOG_DIR/gumpy.html
export GUMP_PROFILE_LOG_DIR=$GUMP_LOG_DIR/myprofile

if [ -z "$GUMP_WORKSPACE" ] ; then
	export GUMP_WORKSPACE=${GUMP_HOST}
fi

export SEPARATOR='------------------------------------------------------- G U M P Y'

#
# Ensure directory structure to write into 
#
cd $GUMP
if [ ! -d $GUMP_LOG_DIR ] ; then
	mkdir $GUMP_LOG_DIR; 
fi
if [ ! -d $GUMP_LOG_DIR ] ; then
	echo "Failed to create the directory \$GUMP_LOG_DIR variable, can't continue."
	exit 1
fi


#
# Generate gumpy.html from this (into the WWW site)
#
umask 002
echo \<XMP\> > $GUMP_LOG

echo $SEPARATOR >> $GUMP_LOG
echo $SEPARATOR >> $GUMP_LOG
echo "Gump run on $GUMP_HOST at $GUMP_DATE" >> $GUMP_LOG
echo >> $GUMP_LOG
echo "GUMP TARGET : $GUMP_TARGET" >> $GUMP_LOG
echo >> $GUMP_LOG
echo "GUMP        : $GUMP" >> $GUMP_LOG
echo "GUMP W/S    : $GUMP_WS" >> $GUMP_LOG
echo "GUMP LOG    : $GUMP_LOG_DIR" >> $GUMP_LOG
echo >> $GUMP_LOG
echo $SEPARATOR >> $GUMP_LOG
echo "GUMPY.sh version $GUMPY_VERSION" >> $GUMP_LOG
echo $SEPARATOR >> $GUMP_LOG
echo >> $GUMP_LOG

#
# Store the profile (into a myprofile dir)
#

if [ ! -d $GUMP_PROFILE_LOG_DIR ] ; then
	mkdir $GUMP_PROFILE_LOG_DIR; 
fi
if [ ! -d $GUMP_PROFILE_LOG_DIR ] ; then
	exit 1
fi

cp $GUMP/gumpy.sh $GUMP_PROFILE_LOG_DIR
cp $GUMP_HOST.xml  $GUMP_PROFILE_LOG_DIR
if [ -e $LOCAL_ENV ] ; then
	cp $LOCAL_ENV $GUMP_PROFILE_LOG_DIR
fi
if [ -e $HOST_LOCAL_ENV ] ; then
	cp $HOST_LOCAL_ENV $GUMP_PROFILE_LOG_DIR
fi

cp -R `grep profile $GUMP_HOST.xml  | cut -d\" -f2` $GUMP_PROFILE_LOG_DIR

#
##########################################################
#
# Preliminary cleanup
#

# Gump-level tmp
if [ -d $GUMP_TMP ] ; then
	rm -f $GUMP_TMP/*.txt
fi
# Gump work tmp
if [ -d $GUMP_WS_TMP ] ; then
	rm -f $GUMP_WS_TMP/*.txt
fi
# Clear the forrest build area...
if [ -d $GUMP_WS/forrest/build/ ] ; then
	rm -rf $GUMP_WS/forrest/build/
fi

#
###########################################################
# Do a CVS update
#
echo $SEPARATOR >> $GUMP_LOG
cd $GUMP
cvs -q update -dP >> $GUMP_LOG 2>&1 
rm -f .timestamp


#
# Set the PYTHONPATH
#
export PYTHONPATH=$GUMP_PYTHON

#
# Capture environment
#
echo $SEPARATOR >> $GUMP_LOG
export >> $GUMP_LOG
# Capture Python Version
python -V >> $GUMP_LOG 2>&1

#
#
#
cd $GUMP_PYTHON
echo $SEPARATOR >> $GUMP_LOG
echo "Clean *.pyc files." >> $GUMP_LOG
find $GUMP_PYTHON -name '*.pyc' -exec rm {} \;

#
# Do the integration run
#
cd $GUMP_PYTHON
echo $SEPARATOR >> $GUMP_LOG
python gump/integrate.py -w ../${GUMP_WORKSPACE}.xml ${GUMP_TARGET}  "$@" >> $GUMP_LOG 2>&1 
export INTEGRATION_EXIT=$?
echo "Integration completed with exit code : " ${INTEGRATION_EXIT} >> $GUMP_LOG
if [ ${INTEGRATION_EXIT} -gt 0 ] ; then
        echo "Failed to integrate, exited with [${INTEGRATION_EXIT}], exiting..." >> $GUMP_LOG
        echo "Failed to integrate, exited with [${INTEGRATION_EXIT}], exiting..."
        # For cron to mail to owner...
        cat $GUMP_LOG
        exit 1
fi;

echo >> $GUMP_LOG

# 
cd $GUMP_TMP
echo $SEPARATOR >> $GUMP_LOG
if [ -f check_forrest.txt ] ; then
	cat check_forrest.txt >> $GUMP_LOG
	cp check_forrest.txt $GUMP_LOG_DIR
else
	echo "No Forrest Output file @ $GUMP_TMP/check_forrest.txt" >> $GUMP_LOG
fi

echo $SEPARATOR >> $GUMP_LOG

if [ -f forrest.txt ] ; then
	cat forrest.txt >> $GUMP_LOG
	cp forrest.txt $GUMP_LOG_DIR
else
	echo "No Forrest Output file @ $GUMP_TMP/forrest.txt" >> $GUMP_LOG
fi
echo $SEPARATOR >> $GUMP_LOG

if [ -f $GUMP_WS/forrest/build/tmp/brokenlinks.txt ] ; then
	echo $SEPARATOR >> $GUMP_LOG
	cat $GUMP_WS/forrest/build/tmp/brokenlinks.txt >> $GUMP_LOG
	echo $SEPARATOR >> $GUMP_LOG
	cp $GUMP_WS/forrest/build/tmp/brokenlinks.txt $GUMP_LOG_DIR
fi

# Just in case...
cd $GUMP

echo \</XMP\> >> $GUMP_LOG

#
# Ensure nothing we started (directly) is left running after we end...
#
pkill -KILL -P $$ 

# $Log: gumpy.sh,v $
