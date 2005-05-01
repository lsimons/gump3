#!/bin/bash

# Simple script to find all "TODO" lines in python code and e-mail them

GUMP_HOME=/home/gump3/Gump3/bin
cd $GUMP_HOME
svn update -q --non-interactive

COLUMS=300
todos=`find . -name '*.py' -not -path '*.svn*' -not -path '*pygump/work*' -exec grep -nH TODO \{\} \; 2>&1`

subject="TODOs in Gump3 Report"

body="This is an auto-generated report providing a list of all TODOs in the Gump3 codebase.
It is run once a week using the bin/find-todo.sh script. Here's the list:

$todos

best regards,

- gump3@brutus
"

echo "$body" | mail -s "$subject" general@gump.apache.org
