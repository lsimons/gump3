# export JAXP=/opt/jaxp-1.1
# export CLASSPATH=$JAXP/crimson.jar:$JAXP/jaxp.jar:$JAXP/xalan.jar:$CLASSPATH

export XALAN=/opt/xalan-j_2_2_D8

if test "$1" = "-cp"; then
  shift
  export CP="$1"
  shift
fi

test -n "$1" && export SOURCE=$1

if test "$OSTYPE" = "cygwin32" -o "$OSTYPE" = "cygwin"; then
  export CLASSPATH=`cygpath --path --unix "$CLASSPATH"`
  export CLASSPATH=.:jenny.jar:$XALAN/bin/xerces.jar:$XALAN/bin/xalan.jar:$CLASSPATH
  export CLASSPATH=`cygpath --path --windows "$CLASSPATH"`
else
  export CLASSPATH=.:jenny.jar:$XALAN/bin/xerces.jar:$XALAN/bin/xalan.jar:$CLASSPATH
fi

test -z "$1" && export SOURCE=`hostname | sed s/[.].*//`.xml
test -d work && rm -rf work
mkdir work

# ********************************************************************

echo Merging projects into workspace
rm -rf classes
mkdir classes
javac -d classes java/*.java || export FAIL=1
jar cf jenny.jar -C classes . || export FAIL=1
echo
java -classpath "$CLASSPATH" Jenny $SOURCE || export FAIL=1

# ********************************************************************

echo Generate checkout instructions
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -xml -in work/sorted.xml -xsl stylesheet/update.xsl -out work/update.xml || \
export FAIL=1

echo Applying web site stylesheet
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -xml -in work/update.xml -xsl stylesheet/jakarta.xsl -out work/updatesite.xml || \
export FAIL=1

echo Generating update script
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -text -in work/updatesite.xml -xsl stylesheet/bash.xsl -out work/update.sh -PARAM cmd-prefix "$CP" -PARAM os-type "$OSTYPE" || \
export FAIL=1

# ********************************************************************

echo Generate build instructions
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -xml -in work/sorted.xml -xsl stylesheet/build.xsl -out work/build.xml || \
export FAIL=1

echo Applying web site stylesheet
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -xml -in work/build.xml -xsl stylesheet/jakarta.xsl -out work/buildsite.xml || \
export FAIL=1

echo Generating build script
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -EDUMP -text -in work/buildsite.xml -xsl stylesheet/bash.xsl -out work/build.sh -PARAM cmd-prefix "$CP" -PARAM os-type "$OSTYPE" || \
export FAIL=1

# ********************************************************************

echo Generate crossreference data
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -xml -in work/sorted.xml -xsl stylesheet/xref.xsl -out work/xref.xml || \
export FAIL=1

echo Applying web site stylesheet
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -xml -in work/xref.xml -xsl stylesheet/jakarta.xsl -out work/xrefsite.xml || \
export FAIL=1

echo Generating xref script
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -text -in work/xrefsite.xml -xsl stylesheet/bash.xsl -out work/xref.sh || \
export FAIL=1

# ********************************************************************

echo Generate script to publish all xml source files
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -text -in work/merge.xml -xsl stylesheet/bash.xsl -out work/puball.sh || \
export FAIL=1

echo Generate template for publishing an xml source file
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -xml -in work/sorted.xml -xsl stylesheet/publish.xsl -out work/publish.xml || \
export FAIL=1

echo Applying web site stylesheet
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -xml -in work/publish.xml -xsl stylesheet/jakarta.xsl -out work/pubsite.xml || \
export FAIL=1

echo Generating publish script
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -text -in work/pubsite.xml -xsl stylesheet/bash.xsl -out work/publish.sh || \
export FAIL=1

echo Generate editing instructions
test -n "$FAIL" || \
java org.apache.xalan.xslt.Process -text -in work/merge.xml -xsl stylesheet/sedmap.xsl -out work/map.pl || \
export FAIL=1

# **** publish ***
if test -z "$FAIL"; then
  echo
  echo Publishing
  cd work
  chmod +x *.sh
  bash puball.sh $SOURCE
  cd ..
fi

test -z "$FAIL" || echo "*** FAILED ***"

