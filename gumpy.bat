REM @ECHO OFFF
REM
REM _ J A K A R T A  G U M P _ J A K A R T A  G U M P _ J A K A R T A  G U M P _ 
REM
REM
REM $Header: $
REM
REM
if "%OS%"=="Windows_NT" @SETLOCAL

SET GUMP_HOST=%COMPUTERNAME%
SET LOCAL_ENV=local-env-py.sh
IF EXIST  %LOCAL_ENV% CALL %LOCAL_ENV%

SET HOST_LOCAL_ENV="local-env-py-%GUMP_HOST%.sh"
IF EXIST  %HOST_LOCAL_ENV% CALL %HOST_LOCAL_ENV%

IF NOT "%GUMP%" == "" GOTO hasGumpEnv
	ECHO Set the GUMP variable to your gump install.
	goto end
:hasGumpEnv

IF NOT "%GUMP_WS%" == "" GOTO hasGumpWSEnv
	ECHO Set the GUMP_WS variable to your gump working area.
	goto end
:hasGumpWSEnv

IF NOT "%GUMP_LOG_DIR%" == "" GOTO hasGumpLogDirEnv
	ECHO Set the GUMP_LOG_DIR variable to your gump WWW directory.
	goto end
:hasGumpLogDirEnv

SET GUMP_TARGET=all
IF NOT "" == "%1" SET GUMP_TARGET=%1

REM
REM Calculated
REM
SET GUMPY_VERSION="1.0.6"
SET GUMP_PYTHON=%GUMP%\python
SET GUMP_TMP=%GUMP%\tmp
SET GUMP_WS_TMP=%GUMP_WS%\tmp
SET GUMP_LOG=%GUMP_LOG_DIR%\gumpy.html
SET GUMP_PROFILE_LOG_DIR=%GUMP_LOG_DIR%\myprofile

IF "" == "%GUMP_WORKSPACE%" SET GUMP_WORKSPACE=%GUMP_HOST%

SET SEPARATOR=------------------------------------------------------- G U M P Y

REM
REM Ensure directory structure to write into 
REM
cd %GUMP%
IF NOT EXIST %GUMP_LOG_DIR% MKDIR %GUMP_LOG_DIR%; 
IF EXIST %GUMP_LOG_DIR% goto hasLogDir:
	ECHO "Failed to find/create the directory GUMP_LOG_DIR=%GUMP_LOG_DIR%, can't continue."
	goto end
:hasLogDir

REM
REM Generate gumpy.html from this (into the WWW site)
REM
ECHO "<XMP>" > %GUMP_LOG%
ECHO %SEPARATOR% >> %GUMP_LOG%
ECHO %SEPARATOR% >> %GUMP_LOG%
ECHO "Gump run on %GUMP_HOST% >> %GUMP_LOG%
ECHO "" >> %GUMP_LOG%
ECHO "GUMP TARGET : %GUMP_TARGET%" >> %GUMP_LOG%
ECHO "" >> %GUMP_LOG%
ECHO "GUMP        : %GUMP%" >> %GUMP_LOG%
ECHO "GUMP W/S    : %GUMP_WS%" >> %GUMP_LOG%
ECHO "GUMP LOG    : %GUMP_LOG_DIR%" >> %GUMP_LOG%
ECHO "" >> %GUMP_LOG%
ECHO %SEPARATOR% >> %GUMP_LOG%
ECHO "GUMPY.sh version %GUMPY_VERSION%" >> %GUMP_LOG%
ECHO %SEPARATOR% >> %GUMP_LOG%
ECHO "" >> %GUMP_LOG%

REM
REM Store the profile (into a myprofile dir)
REM

IF NOT EXIST %GUMP_PROFILE_LOG_DIR% MKDIR %GUMP_PROFILE_LOG_DIR% 

IF EXIST %GUMP_PROFILE_LOG_DIR% GOTO hasProfileLogDir
	ECHO "Profile log directory doesn't exists [%GUMP_PROFILE_LOG_DIR%"
	goto end
:hasProfileLogDir

COPY %GUMP%\gumpy.sh %GUMP_PROFILE_LOG_DIR%
COPY %GUMP_HOST%.xml  %GUMP_PROFILE_LOG_DIR%
IF EXIST %LOCAL_ENV% COPY %LOCAL_ENV% %GUMP_PROFILE_LOG_DIR%
IF EXIST %HOST_LOCAL_ENV% COPY %HOST_LOCAL_ENV% %GUMP_PROFILE_LOG_DIR%

REM  :TODO:  cp -R `grep profile %GUMP_HOST%.xml  | cut -d\" -f2` %GUMP_PROFILE_LOG_DIR%

REM
REM
REM Preliminary cleanup
REM

REM Gump-level tmp
IF EXIST %GUMP_TMP% REMOVE %GUMP_TMP%\*.txt

REM Gump work tmp
IF EXIST %GUMP_WS_TMP% REMOVE %GUMP_WS_TMP%\*.txt

REM Clear the forrest build area...
IF EXIST %GUMP_WS%\forrest\build\ REMOVE %GUMP_WS%\forrest\build\

REM
REM Do a CVS update
REM
IF NOT "" == "%GUMP_WITHOUT_CVS_UPDATE" GOTO skipCVSUpdate
ECHO %SEPARATOR% >> %GUMP_LOG%
CD %GUMP%
ECHO "Update Jakarta Gump from CVS" >> %GUMP_LOG%
cvs -q update -dP >> %GUMP_LOG% 2>&1 
REMOVE -f .timestamp
:skipCVSUpdate

REM
REM Set the PYTHONPATH
REM
SET PYTHONPATH=%GUMP_PYTHON%

REM
REM Capture environment
REM
ECHO %SEPARATOR% >> %GUMP_LOG%
SET >> %GUMP_LOG%
REM Capture Python Version
python -V >> %GUMP_LOG% 2>&1

REM
REM
REM
cd %GUMP_PYTHON%
ECHO %SEPARATOR% >> %GUMP_LOG%
ECHO "Clean *.pyc files." >> %GUMP_LOG%
REM find %GUMP_PYTHON% -name '*.pyc' -exec rm {} \;

REM
REM Do the integration run
REM
cd %GUMP_PYTHON%
ECHO %SEPARATOR% >> %GUMP_LOG%
ECHO "Integrate using -w ..\%GUMP_WORKSPACE%.xml %GUMP_TARGET% %2 %3 %4 %5 %6" >> %GUMP_LOG%
python gump\integrate.py -w ..\%GUMP_WORKSPACE%.xml %GUMP_TARGET% %2 %3 %4 %5 %6 >> %GUMP_LOG% 
IF ERRORLEVEL == 0 GOTO integratedOk		
        ECHO "Failed to integrate, exited with error, exiting..." >> %GUMP_LOG%
        ECHO "Failed to integrate, exited with error, exiting..."
        goto end
:integratedOk

ECHO %SEPARATOR% >> %GUMP_LOG%
ECHO >> %GUMP_LOG%

REM 
CD %GUMP_TMP%
ECHO %SEPARATOR% >> %GUMP_LOG%
IF NOT EXIST check_forrest.txt GOTO noCheckForrest
	TYPE check_forrest.txt >> %GUMP_LOG%
	COPY check_forrest.txt %GUMP_LOG_DIR%
	GOTO checkedForrest
:noCheckForrest:
	ECHO "No Forrest Output file @ %GUMP_TMP%\check_forrest.txt" >> %GUMP_LOG%
:checkedForrest

ECHO %SEPARATOR% >> %GUMP_LOG%

IF NOT EXIST forrest.txt GOTO noForrestOutput
	TYPE forrest.txt >> %GUMP_LOG%
	COPY forrest.txt %GUMP_LOG_DIR%
	GOTO forrested
:noForrestOutput
	ECHO "No Forrest Output file @ %GUMP_TMP%\forrest.txt" >> %GUMP_LOG%
:forrested

ECHO %SEPARATOR% >> %GUMP_LOG%

IF NOT EXIST %GUMP_WS%\forrest\build\tmp\brokenlinks.txt GOTO noBrokenLinks
	ECHO %SEPARATOR% >> %GUMP_LOG%
	TYPE %GUMP_WS%\forrest\build\tmp\brokenlinks.txt >> %GUMP_LOG%
	ECHO %SEPARATOR% >> %GUMP_LOG%
	COPY %GUMP_WS%\forrest\build\tmp\brokenlinks.txt %GUMP_LOG_DIR%
:noBrokenLinks

:end

REM Just in case...
IF "" == "%GUMP%" GOTO endedWithoutGump
	CD %GUMP%
:endedWithoutGump

IF "" == "%GUMP_LOG%" GOTO endedWithoutLog
	ECHO "</XMP>" >> %GUMP_LOG%
:endedWithoutLog

if "%OS%"=="Windows_NT" @ENDLOCAL

:mainEnd

REM _ J A K A R T A  G U M P _ J A K A R T A  G U M P _ J A K A R T A  G U M P _ 
REM
REM $Log: gumpy.sh,v $
REM
REM _ J A K A R T A  G U M P _ J A K A R T A  G U M P _ J A K A R T A  G U M P _ 
