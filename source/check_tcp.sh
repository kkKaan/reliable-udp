# checker for tcp, comparing resulting files with reference files

for i in {0..9}
do
    diff received_large-$i.obj large-$i.obj
    if [ $? -eq 0 ]
    then
        echo "large-$i.obj: OK"
    else
        echo "large-$i.obj: FAILED"
    fi
    sleep 0.1
    diff received_small-$i.obj small-$i.obj
    if [ $? -eq 0 ]
    then
        echo "small-$i.obj: OK"
    else
        echo "small-$i.obj: FAILED"
    fi
done
