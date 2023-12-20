#!/bin/bash
x=0
while [ $x -le 9 ]
do
        echo "Generating $x times"
        #truncate -s 10K "small-$x.obj"
        dd if=/dev/urandom bs=7400 count=1 | base64 > "small-$x.obj"
        md5=($(md5sum "small-$x.obj"))
        echo $md5 > "small-$x.obj.md5"
        #truncate -s 10M "large-$x.obj"
        dd if=/dev/urandom bs=740000 count=1 | base64 > "large-$x.obj"
        md5=($(md5sum "large-$x.obj"))
        echo $md5 > "large-$x.obj.md5"
        x=$(( $x + 1 ))
done