@echo off

REM 
REM    Copyright (c) 2000-2003 The Apache Software Foundation.  All rights
REM    reserved.

SET

CD %GUMP_PYTHON%
python gump\test\pyunit.py
