#!/bin/sh

temp_file=$(mktemp --suffix .png -t deskew.XXXXXXXXXX)
convert $1 -thumbnail 1024x1024 $temp_file
convert $temp_file -debug Transform -deskew 10 /dev/null
rm $temp_file
