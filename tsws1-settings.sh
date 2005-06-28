
case "`uname`" in
  CYGWIN*) cygwin=true ;;
esac

if $cygwin; then
  export JAVA_HOME=/cygdrive/f/apps/javasoft/j2sdk1.4.2/
else
  export JAVA_HOME=/usr/lib/j2se/1.4
fi

export PYTHONPATH=$PYTHONPATH:/cygdrive/f/apps/python-irclib-0.4.5/

