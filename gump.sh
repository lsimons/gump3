#!/bin/bash
#
# $Header: $

# nickchalko:  I thnik we can use  if  [-f local_env.sh ] . local_env.sh  to 
# set all the stuff below
# :USER: set GUMP and GUMP WORKSPACE and GUMP LOG DIR here
#export GUMP=
#export GUMP_WS=
#export GUMP_LOG_DIR=
# Examples...
# export GUMP=$HOME/jakarta-gump
# export GUMP_WS=/homelocal/build/gump-ws
# export GUMP_LOG_DIR=$GUMP_WS/www

#
#
# :USER: set your PATH and CLASSPATH and other ENV settings here
# :USER: ... if you need to, for cron etc.
#
# Examples..
#
# export PATH=$GUMP/bin:$JAVA_HOME/bin:/usr/local/bin:$PATH
# export CLASSPATH=$JAVA_HOME/lib/tools.jar
# export CVS_RSH=`which ssh`
# export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib
# export FORREST_HOME=$HOME/xml-forrest/build/dist/shbat

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



#
# Calculated
#
export GUMP_HOST=`hostname -s`
export GUMP_DATE=`date`
export GUMP_LOG=$GUMP_LOG_DIR/gump.html
export GUMP_PROFILE_LOG_DIR=$GUMP_LOG_DIR/myprofile

export SEPARATOR='------------------------------------------------------- G U M P'

#
# Generate gump.html from this (into the WWW site)
#
umask 002
echo \<XMP\> > $GUMP_LOG

echo $SEPARATOR >> $GUMP_LOG
echo $SEPARATOR >> $GUMP_LOG
echo "Gump run on $GUMP_HOST at $GUMP_DATE" >> $GUMP_LOG
echo $SEPARATOR >> $GUMP_LOG
echo $SEPARATOR >> $GUMP_LOG
echo >> $GUMP_LOG

#
# Store the profile (into a myprofile dir)
#
cd $GUMP
if [ ! -d $GUMP_PROFILE_LOG_DIR ] ; then
	mkdir $GUMP_PROFILE_LOG_DIR; 
fi
cp $GUMP/gump.sh $GUMP_PROFILE_LOG_DIR
cp $GUMP_HOST.xml  $GUMP_PROFILE_LOG_DIR
cp `grep profile $GUMP_HOST.xml  | cut -d\" -f2` $GUMP_PROFILE_LOG_DIR

#
# Do a CVS update
#
echo $SEPARATOR >> $GUMP_LOG
cd $GUMP
cd ..
export CVSROOT=:pserver:anoncvs@cvs.apache.org:/home/cvspublic
cvs update  >> $GUMP_LOG 2>&1 
rm -f .timestamp


#
# Check the projects
#
cd $GUMP
echo $SEPARATOR >> $GUMP_LOG
ant check >> $GUMP_LOG 2>&1

#
# Do a gen
#
cd $GUMP
echo $SEPARATOR >> $GUMP_LOG
bash gen.sh tsbuild1.xml >> $GUMP_LOG 2>&1 
echo >> $GUMP_LOG

#
# Do a clean
#
echo $SEPARATOR >> $GUMP_LOG
bash $GUMP_WS/build.sh gump clean >> $GUMP_LOG
echo >> $GUMP_LOG

#
# Capture environment
#
echo $SEPARATOR >> $GUMP_LOG
export >> $GUMP_LOG

# /usr/X11R6/bin/Xvfb :8 &
# export DISPLAY=:8

#
# Do an update (from CVS)
#
cd $GUMP_WS
echo $SEPARATOR >> $GUMP_LOG
bash update.sh all   >> $GUMP_LOG 2>&1 

#
# Do the build
#
cd $GUMP_WS
echo $SEPARATOR >> $GUMP_LOG
bash build.sh all   >> $GUMP_LOG 2>&1 

cd $GUMP
echo $SEPARATOR >> $GUMP_LOG
if [ -n $STARTED_FROM_CRON ] ; then 
	perl nag.pl work/naglist >> $GUMP_LOG 2>&1
fi;

echo \</XMP\> >> $GUMP_LOG
pkill -P $$ 

# $Log: $
