#!/bin/bash
#
# $Header: /home/stefano/cvs/gump/Attic/gumppy.sh,v 1.2 2003/05/30 22:02:56 nickchalko Exp $

if [ -e local-env.sh ] ; then
	. local-env.sh
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
export GUMP_PYTHON=$GUMP/python
export GUMP_HOST=`hostname -s`
export GUMP_DATE=`date`
export GUMP_LOG=$GUMP_LOG_DIR/gumppy.html
export GUMP_PROFILE_LOG_DIR=$GUMP_LOG_DIR/myprofile

export SEPARATOR='------------------------------------------------------- G U M P P Y'

#
# Generate gumppy.html from this (into the WWW site)
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
echo $SEPARATOR >> $GUMP_LOG
echo >> $GUMP_LOG

#
# Store the profile (into a myprofile dir)
#
cd $GUMP
if [ ! -d $GUMP_LOG_DIR ] ; then
	mkdir $GUMP_LOG_DIR; 
fi
if [ ! -d $GUMP_LOG_DIR ] ; then
	exit 1
fi

if [ ! -d $GUMP_PROFILE_LOG_DIR ] ; then
	mkdir $GUMP_PROFILE_LOG_DIR; 
fi
if [ ! -d $GUMP_PROFILE_LOG_DIR ] ; then
	exit 1
fi

cp $GUMP/gumppy.sh $GUMP_PROFILE_LOG_DIR
cp $GUMP_HOST.xml  $GUMP_PROFILE_LOG_DIR
cp `grep profile $GUMP_HOST.xml  | cut -d\" -f2` $GUMP_PROFILE_LOG_DIR

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
cd $GUMP_PYTHON
echo $SEPARATOR >> $GUMP_LOG
python gump/check.py -w ../${GUMP_HOST}.xml >> $GUMP_LOG 2>&1

#
# Do a gen
#
cd $GUMP_PYTHON
echo $SEPARATOR >> $GUMP_LOG
python gump/gen.py -w ../${GUMP_HOST}.xml >> $GUMP_LOG 2>&1 
echo >> $GUMP_LOG

#
# Do a clean
#
#cd $GUMP_PYTHON
#echo $SEPARATOR >> $GUMP_LOG
#python gump/clean.py -w ../${GUMP_HOST}.xml >> $GUMP_LOG 2>&1
#echo >> $GUMP_LOG

#
# Do an update (from CVS)
#
cd $GUMP_PYTHON
echo $SEPARATOR >> $GUMP_LOG
python gump/update.py -w ../${GUMP_HOST}.xml $GUMP_TARGET >> $GUMP_LOG 2>&1 

#
# Do the build
#
cd $GUMP_PYTHON
echo $SEPARATOR >> $GUMP_LOG
python gump/build.py -w ../${GUMP_HOST}.xml $GUMP_TARGET >> $GUMP_LOG 2>&1 

#
# Nag (if required)
#
cd $GUMP
echo $SEPARATOR >> $GUMP_LOG
if [ -n "$STARTED_FROM_CRON" ] ; then 
	perl nag.pl work/naglist >> $GUMP_LOG 2>&1
fi;

echo \</XMP\> >> $GUMP_LOG
pkill -P $$ 

# $Log: gumppy.sh,v $
# Revision 1.2  2003/05/30 22:02:56  nickchalko
# Fixing incomplete update from Adam
# PR:
# Obtained from:
# Submitted by:Adam Jack ajack@TrySybase.com
# Reviewed by:
#
