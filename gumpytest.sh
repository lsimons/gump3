#!/bin/bash
#
# This script will self-test Gump (Python) Capabilities
#
#
# $Header$

export

#
# Perform some Gumpy unit test
#
cd $GUMP_PYTHON
python gump/test/pyunit.py