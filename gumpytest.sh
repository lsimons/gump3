#!/bin/bash
#
# This script will self-test Gump (Python) Capabilities
#
#
# $Header: $

export
pwd

#
# Perform some CLASSPATH checks
#
echo "CLASSPATH checks"
python gump/logic.py krysalis-ruper-ant
python gump/logic.py commons-graph