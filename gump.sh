#! /bin/sh
# $Header: $
export JAVA_HOME=/usr/java/j2sdk1.4.1_01
export PATH=/home/nick/gump/bin:$JAVA_HOME/bin:/usr/local/bin:$PATH
export CLASSPATH=$JAVA_HOME/lib/tools.jar
export CVS_RSH=`which ssh`
export LOG_DIR=/var/www/html/gump
#export LOG=/home/nick/gump-log/gen.html
export LOG=/var/www/html/gump/gen.html
export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib
export FORREST_HOME=/home/nick/xml-forrest/build/dist/shbat



umask 002

echo \<XMP\> > $LOG
cd /home/nick/local-gump
#mkdir $LOG_DIR/myprofile
cp csm.xml  $LOG_DIR/myprofile
cp $HOME/cron/gump2.sh $LOG_DIR/myprofile
cvs update  >> $LOG 2>&1 
rm .timestamp
bash gen.sh csm.xml >> $LOG 2>&1 
#echo >> $LOG
#bash work/build.sh gump clean >> $LOG
echo >> $LOG
export >> $LOG

# /usr/X11R6/bin/Xvfb :8 &
# export DISPLAY=:8

cd /home/nick/gump-work/
bash update.sh all   >> $LOG 2>&1 
rm /home/nick/gump-jars
bash build.sh all   >> $LOG 2>&1 

cd $HOME/local-gump/
echo started from cron $STARTED_FROM_CRON
if [ -n $STARTED_FROM_CRON ] ; then 
	perl nag.pl work/naglist >> $LOG 2>&1
fi;

echo \</XMP\> >> $LOG
pkill -P $$ 
