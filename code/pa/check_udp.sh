# checker for udp results

for i in {0..9}
do
    diff udp_large-$i.obj large-$i.obj
    if [ $? -eq 0 ]
    then
        echo "large-$i.obj: OK"
    else
        echo "large-$i.obj: FAILED"
    fi
    sleep 0.1
    diff udp_small-$i.obj small-$i.obj
    if [ $? -eq 0 ]
    then
        echo "small-$i.obj: OK"
    else
        echo "small-$i.obj: FAILED"
    fi
done
