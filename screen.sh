#!/bin/bash

if [ $1 == 'on' ]; then
    tvservice -p
    fbset -depth 8
    fbset -depth 16
    if [ $(whoami) == 'pi' ]; then
        xrefresh -d :0.0
    else
        su pi -c "xrefresh -d :0.0"
    fi
    echo 'Switched Screen ON!'
fi

if [ $1 == 'off' ]; then
    tvservice -o
    echo 'Switched Screen OFF!'
fi