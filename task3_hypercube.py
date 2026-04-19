"""
----------------------------------------------------------------------
PDC Assignment 2 - Section B, Question 3
Hypercube Dimension-Ordered Routing
Student Name: Zeenat Ijaz
Roll Number : 23F-0054
Section     : AI-6A
----------------------------------------------------------------------
"""

import threading
import time
import math
import matplotlib.pyplot as plt

class ZeenatHypercubeExchange:
    def __init__(self, d):
        self.dims = d
        self.procs = 2 ** d
        # Packets stored as dictionaries {target_node: payload}
        # Payload is simply the source node initially
        self.node_buffers = [{target: i for target in range(self.procs) if target != i} for i in range(self.procs)]
        self.temp_buffers = [{} for _ in range(self.procs)]
        
        self.barrier = threading.Barrier(self.procs)
        self.completed = [{} for _ in range(self.procs)]
        
        self.traffic = []

    def exchange_logic(self, p_id):
        curr_buffer = self.node_buffers[p_id]
        
        for k in range(self.dims):
            self.barrier.wait() # sync before calculating step
            
            mask = (1 << (k + 1)) - 1
            partner = p_id ^ (1 << k)
            
            keep_packets = {}
            send_packets = {}
            
            for target, payload in curr_buffer.items():
                if (target & mask) == (p_id & mask):
                    keep_packets[target] = payload
                else:
                    send_packets[target] = payload
                    
            # Exchange
            self.temp_buffers[partner].update(send_packets)
            self.barrier.wait()
            
            if p_id == 0:
                total_transit = sum(len(tb) for tb in self.temp_buffers)
                self.traffic.append(total_transit)
                
            self.barrier.wait()
            
            # Merge
            curr_buffer = keep_packets
            curr_buffer.update(self.temp_buffers[p_id])
            self.temp_buffers[p_id].clear()
            
            self.barrier.wait()
            
        self.completed[p_id] = curr_buffer

    def run(self):
        threads = []
        start = time.time()
        for i in range(self.procs):
            t = threading.Thread(target=self.exchange_logic, args=(i,))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        end = time.time()
        
        # Verify
        valid = True
        for i in range(self.procs):
            if len(self.completed[i]) != self.procs - 1:
                valid = False
        
        print(f"Hypercube d={self.dims} Validation: {'PASSED' if valid else 'FAILED'}")
        return end - start

    def plot_traffic(self):
        plt.figure(figsize=(7, 4))
        plt.plot(range(1, self.dims + 1), self.traffic, marker='s', color='purple', linestyle='--')
        plt.title(f"Zeenat - Hypercube Network Traffic (d={self.dims})")
        plt.xlabel("Algorithm Step")
        plt.ylabel("Packets in Transit")
        plt.grid(True)
        plt.savefig("z_hypercube_traffic.png")
        plt.close()

if __name__ == '__main__':
    simulator = ZeenatHypercubeExchange(d=4) # 16 nodes
    time_taken = simulator.run()
    simulator.plot_traffic()
    print(f"Total time taken: {time_taken:.5f}s")
