# NAME: Sasubilli Yuvan
# Roll Number:CS20B070
# Course: CS3205 Jan. 2023 semester
# Lab number: 5
# Date of submission: May 1, 2023
# I confirm that the source file is entirely written by me without
# resorting to any dishonest means.
# Website(s) that I used for basic socket programming code are:
# URL(s): geeksforgeeks



from socket import *
import time
import argparse
import _thread
import subprocess
import signal


servers = []  # List to keep track of the server processes


def start_server(serverType, ipaddr, port, *args):
    # Start the server process with extra arguments
    server_process = subprocess.Popen(['python3', serverType , ipaddr , str(port)] + list(args))
    servers.append(server_process)  # Add the server process to the list

def stop_server():
    # ends the processes
    for serverprocess in servers:
        serverprocess.send_signal(signal.SIGTERM)

        
def main():

    global mutex
    global servers


    parser = argparse.ArgumentParser(description='OSPF routing protocol')
    parser.add_argument('-f','--infile', help='Input file', required=True)
    parser.add_argument('-z','--hi', type=int, help='HELLO INTERVAL (in seconds)', required=True)
    parser.add_argument('-a','--lsai', type=int, help='LSA INTERVAL (in seconds)', required=True)
    parser.add_argument('-s','--spfi', type=int, help='SPF INTERVAL (in seconds)', required=True)
    parser.add_argument('-e','--endtime', type=int, help='RUNNING INTERVAL (in seconds)', required=True)
    args = vars(parser.parse_args())

    # set input file
    infile = 'infile.txt'
    infile = args['infile']

    # set hello interval
    hi = 1
    hi = args['hi']

    # set LSA interval
    lsai = 5
    lsai = args['lsai']

    # set SPF interval
    spfi = 20
    spfi = args['spfi']

   
    
   
    input = []
    with open(infile) as f:
        for line in f:
            input.append(line.rstrip('\n').split(' '))
    # set the number of routers
    n_routers = int(input[0][0])


    for i in range(n_routers):
        start_server('rout.py', 'localhost', 10000 + i, str(i), str(n_routers), str(hi), str(lsai), str(spfi) , infile)
        time.sleep(0.1)
        
    start_time = time.time()

    while time.time() - start_time < args['endtime']+5:
        pass
    
    stop_server()

    print("Done")

if __name__ == "__main__":
    main()


    