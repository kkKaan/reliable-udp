# First run client.py and wait for it to finish

for i in {1..5}
do
    sleep 0.2
    rm -f total_time.txt
    # Run client.py
    python3 client.py

    # run sum_times.py
    python3 sum_times.py
done
