#! /bin/bash

if [ -z $1 ]; then
  echo Usage:
  echo    ./findproject.sh PATTERN
  exit 1
fi

if [ ! -d work ]; then
  ant gen
fi

cat work/*.xml | grep '<project' | \
   grep -o ' name="[a-zA-Z0-9_-]*"' | \
   grep -o '"[a-zA-Z0-9_-]*"' | sed -r 's/"//g' | grep $1
