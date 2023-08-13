# NAME: Sasubilli Yuvan
# Roll Number:CS20B070
# Course: CS3205 Jan. 2023 semester
# Lab number: 5
# Date of submission: May 1, 2023
# I confirm that the source file is entirely written by me without
# resorting to any dishonest means.
# Website(s) that I used for basic socket programming code are:
# URL(s): geeksforgeeks


import threading
import time
from collections import defaultdict
from heapq import heappop, heappush
import random
from socket import *
import sys
import _thread
mutex = _thread.allocate_lock()

# mutex = _thread.allocate_lock()


def print_solution(self,start_vertex, distances, parents):
    global mutex
    n_vertices = len(distances)
    
	# self.writeout.write("dest\t\t\t distance\t\tpath")
    
    with open(f'outfile-{self.id}.txt', 'a') as f:
            mutex.acquire()
            f.write("dest\t distance\tpath")  
            mutex.release()         
            for vertex_index in range(n_vertices):
                mutex.acquire()
                if vertex_index != start_vertex:
                    f.write("\n"+ str(vertex_index)+ "\t\t\t\t"+ str(distances[vertex_index])+ "\t\t ")
                    time.sleep(0.1)
                    print_path(self,vertex_index, parents)
                mutex.release()

def print_path(self,current_vertex, parents):
    if current_vertex == -1:
        with open(f'outfile-{self.id}.txt', 'a') as f:
            f.write("end\n")
            f.close()
        return
    print_path(self,parents[current_vertex], parents)
    if True:
        with open(f'outfile-{self.id}.txt', 'a') as f:
            f.write(str(current_vertex)+ " -> ")

class Router:
    def __init__(self, id, n_router, x, y, z, neighbors, links):
        self.id = id # router id
        self.x = x # hello interval
        self.y = y # lsa interval
        self.z = z # spf interval
        # self.outfile = f'router{self.id}.txt' # output file
        self.n_router = n_router # number of routers
        self.neighbors = neighbors # list of neighbors
        self.links = links # links between routers
        self.routing_table = {} # routing table
        self.topology = defaultdict(list) # topology graph
        self.udp_socket = socket(AF_INET, SOCK_DGRAM) # UDP socket
        self.udp_socket.bind(('localhost', 10000 + id)) # bind UDP socket to port 10000 + id
        self.seq_num = 0 # sequence number for LSA packets
        self.lsa_seq_nums = {} # sequence numbers for LSA packets from each router
        self.adj_mat = [] # costs to each neighbors in adjacency matrix
        # self.writeout = open(self.outfile, "w") # output file

    def initialize_adj_mat(self):
        for i in range(int(self.n_router)):
            l=[]
            for j in range(int(self.n_router)):
                l.append(-1)
            self.adj_mat.append(l)
        for i in range(int(self.n_router)):
            self.adj_mat[i][i] = 0

    def update_costs_adj_mat(self,message):
        id1 = int(message[1])
        n = int(message[3])
        i = 4
        for j in range(n):
            id2 = int(message[i])
            weight = int(message[i+1])
            self.adj_mat[id1][id2] = weight
            self.adj_mat[id2][id1] = weight
            i+=2 

    def send_hello(self):
        while True: # send HELLO message to all neighbors doubt :- whether race condition takes place or not
            for neighbor in self.neighbors:
                message = f'HELLO {self.id}' # send HELLO message to neighbor
                self.udp_socket.sendto(message.encode(), ('localhost', 10000 + neighbor)) 
            time.sleep(self.x) # sleep for x seconds


    def receive(self):
        while True:
            data, addr = self.udp_socket.recvfrom(1024) # receive message from neighbor
            message = data.decode() # decode message
            msg = message.split(' ')
            if msg[0] == 'HELLOREPLY':
                parts = message.split() # split message into parts
                src_id = int(parts[-3]) # get source id
                dst_id = int(parts[-2]) # get destination id
                cost = int(parts[-1]) # get cost
                if dst_id == self.id: # if destination id is this router
                    self.adj_mat[src_id][dst_id] = cost
                    self.adj_mat[dst_id][src_id] = cost


            elif msg[0] == 'HELLO': # if message is HELLO
                neighbor_id = int(message.split()[-1]) # get neighbor id
                cost = random.randint(self.links[neighbor_id][0], self.links[neighbor_id][1]) # get cost
                reply_message = f'HELLOREPLY {self.id} {neighbor_id} {cost}' # create HELLOREPLY message
                self.udp_socket.sendto(reply_message.encode(), addr) # send HELLOREPLY message to neighbor


            elif msg[0] == "LSA":
                lsa_message = message # get LSA packet
                lsa_packet = lsa_message.split() # split LSA packet into parts
                src_id = int(lsa_packet[1]) # get source id
                seq_num = int(lsa_packet[2]) # get sequence number
                n_entries = int(lsa_packet[3]) # get number of entries
                # if sequence number is greater than current sequence number
                if src_id not in self.lsa_seq_nums or seq_num > self.lsa_seq_nums[src_id]: 
                    self.lsa_seq_nums[src_id] = seq_num # update sequence number
                    self.update_costs_adj_mat(lsa_packet)
                    edges = [] # list of edges
                    for i in range(n_entries): # add edges to list of edges
                        neighbor_id = int(lsa_packet[4 + i * 2]) 
                        cost = int(lsa_packet[5 + i * 2]) 
                        edges.append((neighbor_id, cost)) # add edge to list of edges
                    self.topology[src_id] = edges # add edges to topology graph
                    for i in self.neighbors: # send LSA packet to all neighbors
                        if i != src_id and i != self.id: # except source and this router
                            self.udp_socket.sendto(lsa_message.encode(), ('localhost', 10000 + i)) # forward LSA packet
                    


            
    def send_lsa(self):
        while True:
            lsa_packet = [f'LSA {self.id} {self.seq_num} {len(self.neighbors)}'] # create LSA packet
            for i in self.neighbors: # add neighbors to LSA packet
                cost = self.adj_mat[self.id][i] # get cost to neighbor
                lsa_packet.append(f'{i} {cost}') # add neighbor id and cost to LSA packet
            lsa_message = ' '.join(lsa_packet) # join LSA packet into string
            for router_id in self.neighbors: # send LSA packet to all routers
                self.udp_socket.sendto(lsa_message.encode(), ('localhost', 10000 + router_id)) # send LSA packet
            self.seq_num += 1 # increment sequence number
            time.sleep(self.y) # sleep for y seconds


    def compute_routing_table(self):
        while True:
            time.sleep(self.z) # sleep for z seconds
            print("This thread is being executed by router_{}".format(self.id))
            with open(f'outfile-{self.id}.txt', 'a') as f:
                    f.write(f'\nTime stamp for router_{self.id} is {time.ctime()}\n')
            f.close()
            # print(f'Time stamp for router_{self.id} is {time.ctime()}\n')
            #dijkstra code here
            shortest_distances = [sys.maxsize] * self.n_router
            
            added = self.n_router * [False]
            
            for vertex_index in range(self.n_router):
                shortest_distances[vertex_index] = sys.maxsize
                added[vertex_index] = False                
            
            shortest_distances[self.id] = 0
            
            parents = [-1] * self.n_router
            
            parents[self.id] = -1
            
            for i in range(1, self.n_router):
                nearest_vertex = -1
                shortest_distance = sys.maxsize
                for vertex_index in range(self.n_router):
                    if not added[vertex_index] and shortest_distances[vertex_index] < shortest_distance:
                        nearest_vertex = vertex_index
                        shortest_distance = shortest_distances[vertex_index]

                added[nearest_vertex] = True

                for vertex_index in range(self.n_router):
                    edge_distance = self.adj_mat[nearest_vertex][vertex_index]                    
                    if edge_distance > 0 and shortest_distance + edge_distance < shortest_distances[vertex_index]:
                        parents[vertex_index] = nearest_vertex
                        shortest_distances[vertex_index] = shortest_distance + edge_distance
                                        
            print_solution(self,self.id, shortest_distances, parents)


    def start_threads(self):
        t0 = threading.Thread(target=self.receive)
        t1 = threading.Thread(target=self.send_hello)
        t2 = threading.Thread(target=self.send_lsa)
        t3 = threading.Thread(target=self.compute_routing_table)
        t0.start()
        t1.start()
        t2.start()
        t3.start()
        t0.join()
        t1.join()
        t2.join()
        t3.join()



args = sys.argv[1:]
serverAddr = args[0]
serverPort = int(args[1])
id = int(args[2])

# set routers count
n_router = int(args[3])

# set hello interval
hi = 1
hi = int(args[4])

# set LSA interval
lsai = 5
lsai = int(args[5])

# set SPF interval
spfi = 20
spfi = int(args[6])

# read input file
infile = args[7]

links = {} # Dictionary to keep track of the routers
neighbors = {} # Dictionary to keep track of the neighbour

with open(infile, 'r') as f:
    lines = f.readlines()
    n_routers, n_links = map(int, lines[0].split())

    for i in range(n_routers):
        links[i] = {}
        neighbors[i] = []

    for line in lines[1:]:
        i, j, min_cij, max_cij = map(int,line.split())
        links[i][j] = (min_cij,max_cij)
        links[j][i] = (min_cij,max_cij)
        neighbors[i].append(j)
        neighbors[j].append(i)


# initialize
r = Router(id, n_router, hi, lsai, spfi, neighbors[id], links[id])
r.initialize_adj_mat()
# start threads
r.start_threads()


    


