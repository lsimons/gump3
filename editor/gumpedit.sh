#!/bin/sh

cygwin=false
case "`uname`" in
  CYGWIN*) cygwin=true ;;
esac

LOCALCLASSPATH=
DIRLIBS=lib/*.jar
for i in ${DIRLIBS}
do
  if [ "$i" != "${DIRLIBS}" ] ; then
    LOCALCLASSPATH=$LOCALCLASSPATH:"$i"
  fi
done

if $cygwin ; then
  CLASSPATH=`cygpath --path --unix "$CLASSAPTH"`
fi

CLASSPATH=$LOCALCLASSPATH:$CLASSPATH

if $cygwin ; then
  CLASSPATH=`cygpath --path --windows "$CLASSPATH"`
fi

java -cp $CLASSPATH org.jbrix.gui.app.Application -a gumpedit.app

