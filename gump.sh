#!/bin/bash
#
# $Header: /home/cvs/jakarta-gump/gump.sh,v 1.7 2003/06/02 18:18:44 nickchalko Exp $

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

echo "Gump Target : $GUMP_TARGET" >> $GUMP_LOG
echo "Gump Location : $GUMP" >> $GUMP_LOG
echo "Gump Workspace : $GUMP_WS" >> $GUMP_LOG
echo "Gump Log : $GUMP_LOG" >> $GUMP_LOG

echo $SEPARATOR >> $GUMP_LOG
echo $SEPARATOR >> $GUMP_LOG
echo >> $GUMP_LOG

#
# Capture environment
#
echo $SEPARATOR >> $GUMP_LOG
export >> $GUMP_LOG

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
cvs -q update -dP >> $GUMP_LOG 2>&1 
rm -f .timestamp

#
# generate nobuild projects
#
cd $GUMP
echo $SEPARATOR >> $GUMP_LOG
ant nobuild-projects >> $GUMP_LOG 2>&1

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
bash gen.sh ${GUMP_HOST}.xml >> $GUMP_LOG 2>&1 
echo >> $GUMP_LOG

#
# Do a clean
#
echo $SEPARATOR >> $GUMP_LOG
bash $GUMP_WS/build.sh clean >> $GUMP_LOG
echo >> $GUMP_LOG

#
# Do an update (from CVS)
#
cd $GUMP_WS
echo $SEPARATOR >> $GUMP_LOG
bash update.sh $GUMP_TARGET   >> $GUMP_LOG 2>&1 

#
# Do the build
#
cd $GUMP_WS
echo $SEPARATOR >> $GUMP_LOG
bash build.sh $GUMP_TARGET   >> $GUMP_LOG 2>&1 

cd $GUMP
echo $SEPARATOR >> $GUMP_LOG
if [ -n "$STARTED_FROM_CRON" ] ; then 
	perl nag.pl work/naglist >> $GUMP_LOG 2>&1
fi;

echo \</XMP\> >> $GUMP_LOG
pkill -P $$ 

# $Log: gump.sh,v $
# Revision 1.7  2003/06/02 18:18:44  nickchalko
# Fixed typo.  $ should be inside the ""
# PR:
# Obtained from: Adam Jack ajack@TrySybase.com
# Submitted by:
# Reviewed by:
#
# Revision 1.6  2003/05/30 22:02:56  nickchalko
# Fixing incomplete update from Adam
# PR:
# Obtained from:
# Submitted by:Adam Jack ajack@TrySybase.com
# Reviewed by:
#
# Revision 1.4  2003/04/09 07:31:42  nickchalko
# -mRemoved reference to tsbuild1
#
# Revision 1.3  2003/04/09 07:27:27  nickchalko
# Moved user specific vars to local-env.sh which is not checked in.
#
# Revision 1.2  2003/04/08 19:18:58  nickchalko
# Here is adams rework.  I moved the cvs log to the bottom, and added a comment about using a local_env.sh file.
#
#
# Commit notes from Adam Jack:
#
# I've taken your enhancements and tried to go one step further.
#
# I have this accepting three environment variables GUMP/GUMP_WS/GUMP_LOG and
# try to do everything off those. It exits (with 1 -- that right?) if they are
# not set. I set those three and it seems to run in my environment. Normally
# I'd expect folks to hack these entries.
#
# 1) I have it copy `hostname -s`.xml (likely workspace) and 'likely profile'
# and the gump.sh to myprofile:
#
# 	cp $GUMP/gump.sh $GUMP_PROFILE_LOG_DIR
# 	cp $GUMP_HOST.xml  $GUMP_PROFILE_LOG_DIR
# 	cp `grep profile $GUMP_HOST.xml  | cut -d\" -f2` $GUMP_PROFILE_LOG_DIR
#
# 2) I added some CVS headers, but am not sure I got those right.
#
# 3) I set it as bash not sh -- that ok?
#
# 4) I made it echo some separators, but it could use more verbose information
# about each section.
#
# 5) I made the output be gump.html (better name than gen.html).
#
# 6) I don't like the way cron is detected (for running nag.pl) something
# better is needed.
#
# 7) I made it do the CVS update each time, and a build clean each time. Maybe
# these are overkill.
#
# This is a major work in progress (it'd be nice if it output HTML as pretty
# as build.sh or update.sh) and it needs a few switches (so folks don't have
# to do everything every time.)
#
# This is is "Linux" format.
#
#
# Submitted by:	Adam Jack ajack@TrySybase.com
#
