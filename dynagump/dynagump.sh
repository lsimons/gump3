#!/bin/sh
#
# Configuration variables
#
# JAVA_HOME
#   Home of Java installation.
#
# JAVA_OPTIONS
#   Extra options to pass to the JVM
#
# JETTY_PORT
#   Override the default port for Jetty
# 
# JETTY_ADMIN_PORT
#   The port where the jetty web administration should bind
#
# JAVA_DEBUG_PORT
#   The location where the JVM debug server should listen to
#

usage()
{
    echo "Usage: $0 (action)"
    echo "actions:"
    echo "  run       Run in a servlet container"
    echo "  admin     Run in a servlet container and turn on container web administration"
    echo "  debug     Run in a servlet container and turn on JVM remote debug"
    echo "  profile   Run in a servlet container and turn on JVM profiling"
    exit 1
}

[ $# -gt 0 ] || usage

ACTION=$1
shift
ARGS="$*"

# ----- Verify and Set Required Environment Variables -------------------------

if [ "$JAVA_HOME" = "" ] ; then
  echo You must set JAVA_HOME to point at your Java Development Kit installation
  exit 1
fi

if [ "$JAVA_OPTIONS" = "" ] ; then
  JAVA_OPTIONS='-Djava.awt.headless=true -Xms32M -Xmx64M'
fi

if [ "$JETTY_PORT" = "" ] ; then
  JETTY_PORT='8080'
fi

if [ "$JETTY_ADMIN_PORT" = "" ] ; then
  JETTY_ADMIN_PORT='8081'
fi

if [ "$JAVA_DEBUG_PORT" = "" ] ; then
  JAVA_DEBUG_PORT='8082'
fi

# ----- Set platform specific variables

PATHSEP=":";
case "`uname`" in
   CYGWIN*) PATHSEP=";" ;;
esac

# ----- Set Local Variables ( used to minimize cut/paste) ---------------------

JAVA="$JAVA_HOME/bin/java"
ENDORSED_LIBS="./tools/jetty/lib/endorsed"
ENDORSED="-Djava.endorsed.dirs=$ENDORSED_LIBS"
PARSER=-Dorg.xml.sax.parser=org.apache.xerces.parsers.SAXParser
LOADER=Loader
LOADER_LIB="./tools/loader"

JETTY=-Dloader.main.class=org.mortbay.jetty.Server
JETTY_CONF="./tools/jetty/conf"
JETTY_MAIN="$JETTY_CONF/main.xml"
JETTY_ADMIN="$JETTY_CONF/admin.xml"
JETTY_WEBAPP="-Dwebapp=./webapp"
JETTY_HOME="-Dhome=."
JETTY_PORT_ARGS="-Djetty.port=$JETTY_PORT"
JETTY_ADMIN_ARGS="-Djetty.admin.port=$JETTY_ADMIN_PORT"
JETTY_LIBRARIES="-Dloader.jar.repositories=./tools/jetty/lib${PATHSEP}${ENDORSED_LIBS}"

# ----- Do the action ----------------------------------------------------------

case "$ACTION" in
  run)
        $JAVA $JAVA_OPTIONS -cp $LOADER_LIB $ENDORSED $PARSER $JETTY_PORT_ARGS $JETTY_LIBRARIES $JETTY_WEBAPP $JETTY_HOME $JETTY $LOADER $JETTY_MAIN
        ;;

  admin)
        $JAVA $JAVA_OPTIONS -cp $LOADER_LIB $ENDORSED $PARSER $JETTY_PORT_ARGS $JETTY_ADMIN_ARGS $JETTY_LIBRARIES $JETTY_WEBAPP $JETTY_HOME $JETTY $LOADER $JETTY_MAIN $JETTY_ADMIN
        ;;

  debug)
        $JAVA $JAVA_OPTIONS -Xdebug -Xrunjdwp:transport=dt_socket,address=$JETTY_DEBUG_PORT,server=y,suspend=n -cp $LOADER_LIB $ENDORSED $PARSER $JETTY_PORT_ARGS $JETTY_LIBRARIES $JETTY_WEBAPP $JETTY_HOME $JETTY $LOADER $JETTY_MAIN
        ;;

  profile)
        $JAVA $JAVA_OPTIONS -Xrunhprof:heap=all,cpu=samples,thread=y,depth=3 -cp $LOADER_LIB $ENDORSED $PARSER $JETTY_ARGS $JETTY_LIBRARIES $JETTY_WEBAPP $JETTY_HOME $JETTY $LOADER $JETTY_MAIN
        ;;

  *)
        usage
        ;;
esac

exit 0
