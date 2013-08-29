#!/bin/bash

export TARGETDIRECTORY=$HOME/www/pxl/dqm 

#echo "TARGETDIRECTORY:" $TARGETDIRECTORY

if [ ! -d $TARGETDIRECTORY ]; then
    mkdir -p $TARGETDIRECTORY/.style
    echo "Created target directory:" $TARGETDIRECTORY
    cp -R style/* $TARGETDIRECTORY/.style
    echo "Options +Indexes" > $TARGETDIRECTORY/.htaccess
fi

export PATH=$PWD/bin:$PATH


