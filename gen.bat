@echo off
SETLOCAL
SET JAXP=C:\jaxp-1.1

SET CLASSPATH=%JAXP%\crimson.jar;%JAXP%\jaxp.jar;%JAXP%\xalan.jar;%CLASSPATH%

SET SOURCE=%1
IF "%1"=="" SET SOURCE=%COMPUTERNAME%.xml

if exist work rmdir /s /q work
mkdir work

echo Merging projects into workspace
java org.apache.xalan.xslt.Process -xml -in %SOURCE% -xsl stylesheet\merge.xsl -out work/merge.xml
if not errorlevel 0 goto fail

echo Sorting projects into dependency order
java org.apache.xalan.xslt.Process -xml -in work\merge.xml -xsl stylesheet\sortdep.xsl -out work\sorted.xml
if not errorlevel 0 goto fail

REM ********************************************************************

echo Generating checkout instructions
java org.apache.xalan.xslt.Process -xml -in work\sorted.xml -xsl stylesheet\update.xsl -out work\update.xml
if not errorlevel 0 goto fail

echo Applying web site stylesheet
java org.apache.xalan.xslt.Process -EDUMP -xml -in work\update.xml -xsl stylesheet\jakarta.xsl -out work\updatesite.xml
if not errorlevel 0 goto fail

echo Generating update script
java org.apache.xalan.xslt.Process -EDUMP -text -in work\updatesite.xml -xsl stylesheet\win2k.xsl -out work\update.bat
if not errorlevel 0 goto fail

REM ********************************************************************

echo Generating build definition
java org.apache.xalan.xslt.Process -EDUMP -indent 2 -xml -in work\sorted.xml -xsl stylesheet\build.xsl -out work\build.xml
if not errorlevel 0 goto fail

echo Applying web site stylesheet
java org.apache.xalan.xslt.Process -EDUMP -xml -in work\build.xml -xsl stylesheet\jakarta.xsl -out work\buildsite.xml
if not errorlevel 0 goto fail

echo Generating build script
java org.apache.xalan.xslt.Process -EDUMP -text -in work\buildsite.xml -xsl stylesheet\win2k.xsl -out work\build.bat
if not errorlevel 0 goto fail

REM ********************************************************************

echo Generate crossreference data
java org.apache.xalan.xslt.Process -xml -in work\merge.xml -xsl stylesheet\xref.xsl -out work\xref.xml
if not errorlevel 0 goto fail

echo Applying web site stylesheet
java org.apache.xalan.xslt.Process -EDUMP -xml -in work\xref.xml -xsl stylesheet\jakarta.xsl -out work\xrefsite.xml
if not errorlevel 0 goto fail

echo Generating xref script
java org.apache.xalan.xslt.Process -EDUMP -text -in work\xrefsite.xml -xsl stylesheet\win2k.xsl -out work\xref.bat
if not errorlevel 0 goto fail

REM ********************************************************************

echo Generate script to publish all xml source files
java org.apache.xalan.xslt.Process -text -in %SOURCE% -xsl stylesheet\win2k.xsl -out work\puball.bat
if not errorlevel 0 goto fail

echo Generate template for publishing an xml source file
java org.apache.xalan.xslt.Process -xml -in work\merge.xml -xsl stylesheet\publish.xsl -out work\publish.xml
if not errorlevel 0 goto fail

echo Applying web site stylesheet
java org.apache.xalan.xslt.Process -EDUMP -xml -in work\publish.xml -xsl stylesheet\jakarta.xsl -out work\pubsite.xml
if not errorlevel 0 goto fail

echo Generating publish script
java org.apache.xalan.xslt.Process -EDUMP -text -in work\pubsite.xml -xsl stylesheet\win2k.xsl -out work\publish.bat
if not errorlevel 0 goto fail

echo Generate editing instructions
java org.apache.xalan.xslt.Process -text -in %SOURCE% -xsl stylesheet\sedmap.xsl -out work\map.sed
if not errorlevel 0 goto fail

REM ********************************************************************

echo Publishing
cd work
puball %SOURCE%
cd ..

goto eof
:fail
echo *** FAILED ***
:eof

ENDLOCAL
