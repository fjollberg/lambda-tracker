#!/bin/bash

set -e

builddir=dist

# Set cwd to root folder when building.
pushd ${0%/*}

rm -rf $builddir
mkdir -p $builddir
pip3 install --target $builddir sqlalchemy pymysql

zip function.zip track.py
(cd $builddir; zip -r9 ../function.zip .)

popd
