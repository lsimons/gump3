@echo off
::
:: Configuration variables
::
:: JAVA_HOME
::   Home of Java installation.
::
:: JAVA_OPTIONS
::   Extra options to pass to the JVM
::
:: JETTY_PORT
::   Override the default port for Jetty
::
:: JETTY_ADMIN_PORT
::   The port where the jetty web administration should bind
::
:: JAVA_DEBUG_PORT
::   The location where the JVM debug server should listen to
::

:: ----- Verify and Set Required Environment Variables -------------------------

if not "%JAVA_HOME%" == "" goto gotJavaHome
echo You must set JAVA_HOME to point at your Java Development Kit installation
goto end
:gotJavaHome

:: ----- Check System Properties -----------------------------------------------

if not "%JAVA_OPTIONS%" == "" goto gotJavaOptions
set JAVA_OPTIONS="-Xmx64M -Xms32M"
:gotJavaOptions

if not "%JETTY_PORT%" == "" goto gotJettyPort
set JETTY_PORT=8080
:gotJettyPort

if not "%JETTY_ADMIN_PORT%" == "" goto gotJettyAdminPort
set JETTY_ADMIN_PORT=8081
:gotJettyAdminPort

if not "%JAVA_DEBUG_PORT%" == "" goto gotDebugPort
set JAVA_DEBUG_PORT=8082
:gotDebugPort

set JETTY_WEBAPP=.\webapp

:: ----- Set Up The Classpath --------------------------------------------------

set CP=.\tools\loader

:: ----- Check action ----------------------------------------------------------

if ""%1"" == ""run"" goto doRun
if ""%1"" == ""admin"" goto doAdmin
if ""%1"" == ""debug"" goto doDebug
IF ""%1"" == ""profile"" goto doProfile

echo Usage: longwell (action)
echo actions:
echo   run     Run in a servlet container
echo   admin   Run in a servlet container and turn container web administration on
echo   debug   Run in a servlet container and turn on remote JVM debug
echo   profile Run in a servlet container and turn on JVM profiling
goto end

:: ----- Servlet ---------------------------------------------------------------

:doRun
%EXEC% "%JAVA_HOME%\bin\java.exe" %JAVA_OPTIONS% -classpath "%CP%" "-Djava.endorsed.dirs=.\lib\endorsed" "-Dwebapp=%JETTY_WEBAPP%" -Dorg.xml.sax.parser=org.apache.xerces.parsers.SAXParser -Djetty.port=%JETTY_PORT% -Djetty.admin.port=%JETTY_ADMIN_PORT% "-Dhome=." "-Dloader.jar.repositories=.\tools\jetty\lib;.\lib\endorsed" -Dloader.main.class=org.mortbay.jetty.Server Loader ".\tools\jetty\conf\main.xml"
goto end

:: ----- Servlet with Administration Web Interface -----------------------------

:doAdmin
%EXEC% "%JAVA_HOME%\bin\java.exe" %JAVA_OPTIONS% -classpath "%CP%" "-Djava.endorsed.dirs=.\lib\endorsed" "-Dwebapp=%JETTY_WEBAPP%" -Dorg.xml.sax.parser=org.apache.xerces.parsers.SAXParser -Djetty.port=%JETTY_PORT% -Djetty.admin.port=%JETTY_ADMIN_PORT% "-Dhome=." "-Dloader.jar.repositories=.\tools\jetty\lib;.\lib\endorsed" -Dloader.main.class=org.mortbay.jetty.Server Loader ".\tools\jetty\conf\main.xml" ".\tools\jetty\conf\admin.xml"
goto end

:: ----- Servlet Debug ---------------------------------------------------------

:doDebug
%EXEC% "%JAVA_HOME%\bin\java.exe" %JAVA_OPTIONS% -Xdebug -Xrunjdwp:transport=dt_socket,address=%JAVA_DEBUG_PORT%,server=y,suspend=n  -classpath "%CP%" "-Djava.endorsed.dirs=.\lib\endorsed" "-Dwebapp=%JETTY_WEBAPP%" "-Dhome=." -Dorg.xml.sax.parser=org.apache.xerces.parsers.SAXParser -Djetty.port=%JETTY_PORT% -Djetty.admin.port=%JETTY_ADMIN_PORT% "-Dloader.jar.repositories=.\tools\jetty\lib;.\lib\endorsed" -Dloader.main.class=org.mortbay.jetty.Server Loader ".\tools\jetty\conf\main.xml"
goto end

:: ----- Servlet Profile ---------------------------------------------------------

:doProfile
%EXEC% "%JAVA_HOME%\bin\java.exe" %JAVA_OPTIONS% -Xrunhprof:heap=all,cpu=samples,thread=y,depth=3 -classpath "%CP%" "-Djava.endorsed.dirs=.\lib\endorsed" "-Dwebapp=%JETTY_WEBAPP%" "-Dhome=." -Dorg.xml.sax.parser=org.apache.xerces.parsers.SAXParser -Djetty.port=%JETTY_PORT% -Djetty.admin.port=%JETTY_ADMIN_PORT% "-Dloader.jar.repositories=.\tools\jetty\lib;.\lib\endorsed" -Dloader.main.class=org.mortbay.jetty.Server Loader ".\tools\jetty\conf\main.xml"

:: ----- End -------------------------------------------------------------------

:end
set CP=
set EXEC=
set JAVA_OPTIONS=
set JETTY_PORT=
set JETTY_ADMIN_PORT=
set JETTY_DEBUG_PORT=

