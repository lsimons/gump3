@echo off
@if "%GUMP_ECHO%" == "on" echo %GUMP_ECHO%
SETLOCAL
@REM SET JAXP=C:\jaxp-1.1
@REM 
@REM SET CLASSPATH=%JAXP%\crimson.jar;%JAXP%\jaxp.jar;%JAXP%\xalan.jar;%CLASSPATH%

IF NOT "%XALAN%"=="" SET CLASSPATH=%XALAN%\bin\xml-apis.jar
IF NOT "%XALAN%"=="" SET CLASSPATH=%XALAN%\bin\xalan.jar;%CLASSPATH%
IF NOT "%XALAN%"=="" SET CLASSPATH=%XALAN%\bin\xerces.jar;%CLASSPATH%

SET SOURCE=%1

IF "%1"=="" SET SOURCE=%COMPUTERNAME%.xml

IF "%HOME%"=="" SET HOME=%USERPROFILE%
IF "%HOME%"=="" SET HOME=%HOMEDRIVE%%HOMEPATH%
IF "%HOME%"=="" SET HOME=C:\

if exist work rmdir /s /q work
mkdir work
if not exist cache mkdir cache

@REM ********************************************************************

echo Merging projects into workspace
if exist classes rmdir /s /q classes
mkdir classes
javac -d classes java/*.java
if errorlevel 1 goto fail
jar cf jenny.jar -C classes .
if errorlevel 1 goto fail
echo.
java "-Duser.home=%HOME%" -classpath "jenny.jar;%CLASSPATH%" Jenny %SOURCE%
if not errorlevel 0 goto fail

@REM ********************************************************************

echo Generating checkout instructions
java org.apache.xalan.xslt.Process -xml -in work\merge.xml -xsl stylesheet\update.xsl -out work\update.xml
if not errorlevel 0 goto fail

echo Applying web site stylesheet
java org.apache.xalan.xslt.Process -EDUMP -xml -in work\update.xml -xsl stylesheet\jakarta.xsl -out work\updatesite.xml
if not errorlevel 0 goto fail

echo Generating update script
java org.apache.xalan.xslt.Process -EDUMP -text -in work\updatesite.xml -xsl stylesheet\win2k.xsl -out work\update.bat
if not errorlevel 0 goto fail

@REM ********************************************************************

echo Generating build definition
java org.apache.xalan.xslt.Process -EDUMP -indent 2 -xml -in work\merge.xml -xsl stylesheet\build.xsl -out work\build.xml
if not errorlevel 0 goto fail

echo Applying web site stylesheet
java org.apache.xalan.xslt.Process -EDUMP -xml -in work\build.xml -xsl stylesheet\jakarta.xsl -out work\buildsite.xml
if not errorlevel 0 goto fail

echo Generating build script
java org.apache.xalan.xslt.Process -EDUMP -text -in work\buildsite.xml -xsl stylesheet\win2k.xsl -out work\build.bat
if not errorlevel 0 goto fail

@REM ********************************************************************

echo Generate crossreference data
java org.apache.xalan.xslt.Process -xml -in work\merge.xml -xsl stylesheet\xref.xsl -out work\xref.xml
if not errorlevel 0 goto fail

echo Applying web site stylesheet
java org.apache.xalan.xslt.Process -EDUMP -xml -in work\xref.xml -xsl stylesheet\jakarta.xsl -out work\xrefsite.xml
if not errorlevel 0 goto fail

echo Generating xref script
java org.apache.xalan.xslt.Process -EDUMP -text -in work\xrefsite.xml -xsl stylesheet\win2k.xsl -out work\xref.bat
if not errorlevel 0 goto fail

@REM ********************************************************************

echo Generate script to publish all xml source files
java org.apache.xalan.xslt.Process -text -in work\merge.xml -xsl stylesheet\win2k.xsl -out work\puball.bat
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
java org.apache.xalan.xslt.Process -text -in work\merge.xml -xsl stylesheet\sedmap.xsl -out work\map.pl
if not errorlevel 0 goto fail

echo Generate naglist
java org.apache.xalan.xslt.Process -text -in work\merge.xml -xsl stylesheet\nag.xsl -out work\naglist
if not errorlevel 0 goto fail

echo Generate move instructions for cached files
java org.apache.xalan.xslt.Process -xml -in work\merge.xml -xsl stylesheet\move.xsl -out work\move.xml
if not errorlevel 0 goto fail

echo Generate move script for cached files
java org.apache.xalan.xslt.Process -text -in work\move.xml -xsl stylesheet\win2k.xsl -out work\move.bat
if not errorlevel 0 goto fail

@REM ********************************************************************

echo Publishing
cd work
call puball ..\%SOURCE%
cd ..

echo saving cached files
call work\move.bat

goto eof
:fail
echo *** FAILED ***

:eof

:localcheck
echo.
echo Checking for local dependencies in %SOURCE%
echo.
java "-Duser.home=%HOME%" -classpath "jenny.jar;%CLASSPATH%" LocalCheck %SOURCE%

ENDLOCAL
