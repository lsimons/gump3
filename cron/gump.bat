@ECHO OFF

REM  Copyright 2003-2004 The Apache Software Foundation
REM
REM  Licensed under the Apache License, Version 2.0 (the "License");
REM  you may not use this file except in compliance with the License.
REM  You may obtain a copy of the License at
REM
REM      http://www.apache.org/licenses/LICENSE-2.0
REM
REM  Unless required by applicable law or agreed to in writing, software
REM  distributed under the License is distributed on an "AS IS" BASIS,
REM  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
REM  See the License for the specific language governing permissions and
REM  limitations under the License.
REM
REM _ A P A C H E  G U M P _ A P A C H E   G U M P _ A P A C H E   G U M P _ 
REM
REM
REM $Header:$
REM
REM
if "%OS%"=="Windows_NT" @SETLOCAL

SET GUMP_HOST=%COMPUTERNAME%
SET LOCAL_ENV=local-env.bat
IF EXIST  %LOCAL_ENV% CALL %LOCAL_ENV%

SET HOST_LOCAL_ENV="local-env-%GUMP_HOST%.bat"
IF EXIST  %HOST_LOCAL_ENV% CALL %HOST_LOCAL_ENV%

python gump.py %1 %2 %3 %4 %5

if "%OS%"=="Windows_NT" @ENDLOCAL

:mainEnd

REM _ A P A C H E  G U M P _ A P A C H E   G U M P _ A P A C H E   G U M P _ 
REM
REM $Log: gump.sh,v $
REM
REM _ A P A C H E  G U M P _ A P A C H E   G U M P _ A P A C H E   G U M P _ 
