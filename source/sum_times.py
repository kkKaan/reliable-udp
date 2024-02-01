# Read data from total_time.txt and sum them all, used for UDP.

def sum_times():
    total_time = 0
    with open('total_time.txt', 'r') as f:
        for line in f:
            if float(line) != 0:
                total_time += float(line)
            else:
                # give an error if the time is 0
                print("Error: time is 0")
    return total_time

def main():
    total_time = sum_times()
    print("Total time (ms): ", total_time)
    with open('udp_15loss.txt', 'a') as f: # change filename to where do you want to store 30 test results
        f.write(str(total_time) + '\n')

if __name__ == "__main__":
    main()
