#!/bin/bash
#
# $Header: $

if [ -e local-env-py.sh ] ; then
	. local-env-py.sh
fi

if [ ! $GUMP ] ; then
	echo "Set the \$GUMP variable to your gump install"
	exit 1
fi

if [ ! $GUMP_WS ] ; then
	echo "Set the \$GUMP_WS variable to your gump install"
	exit 1
fi

if [ ! $GUMP_LOG_DIR ] ; then
	echo "Set the \$GUMP_LOG_DIR variable to your gump install"
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
export GUMPY_VERSION="1.0.2"
export GUMP_PYTHON=$GUMP/python
export GUMP_TMP=$GUMP/tmp
export GUMP_HOST=`hostname -s`
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
cp -R `grep profile $GUMP_HOST.xml  | cut -d\" -f2` $GUMP_PROFILE_LOG_DIR

#
# Do a CVS update
#
echo $SEPARATOR >> $GUMP_LOG
cd $GUMP
cvs -q update -dP >> $GUMP_LOG 2>&1 
rm -f .timestamp


#
# Set the PYTHONPATH & cd appropriately
#
export PYTHONPATH=$GUMP_PYTHON

#
# Capture environment
#
echo $SEPARATOR >> $GUMP_LOG
export >> $GUMP_LOG

#
# Check the projects
#
#cd $GUMP_PYTHON
#echo $SEPARATOR >> $GUMP_LOG
#python gump/check.py -w ../${GUMP_WORKSPACE}.xml >> $GUMP_LOG 2>&1

#
# Do the integration run
#
cd $GUMP_PYTHON
echo $SEPARATOR >> $GUMP_LOG
python gump/integrate.py -w ../${GUMP_WORKSPACE}.xml ${GUMP_TARGET} >> $GUMP_LOG 2>&1 
echo >> $GUMP_LOG

# 
cd $GUMP_TMP
echo $SEPARATOR >> $GUMP_LOG
if [ -f forrest.txt ] ; then
	cat forrest.txt >> $GUMP_LOG
else
	echo "No Forrest Output file @ $GUMP_TMP/forrest.txt" >> $GUMP_LOG
fi
echo $SEPARATOR >> $GUMP_LOG

# Just in case...
cd $GUMP

echo \</XMP\> >> $GUMP_LOG
pkill -P $$ 

# $Log: gumpy.sh,v $
# Revision 1.2  2003/05/30 22:02:56  nickchalko
# Fixing incomplete update from Adam
# PR:
# Obtained from:
# Submitted by:Adam Jack ajack@TrySybase.com
# Reviewed by:
#
