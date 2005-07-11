cygwin=""
case "`uname`" in
  CYGWIN*) cygwin="true" ;;
esac

if [[ "$cygwin" == "true" ]]; then
  export JAVA_HOME=/cygdrive/c/j2sdk1.4.2_08
else
  export JAVA_HOME=/usr/lib/j2se/1.5
fi

