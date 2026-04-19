"""
----------------------------------------------------------------------
PDC Assignment 2 - Section B, Question 1
All-to-All Personalized Communication (Ring, Mesh, Hypercube)
Student Name: Zeenat Ijaz
Roll Number : 23F-0054
Section     : AI-6A
----------------------------------------------------------------------
This script executes total exchange algorithms for different
networking topologies, visualizes them, and analyzes performance.
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import math

# =====================================================================
# 1. Topology Generators and Visuals
# =====================================================================

def generate_ring_graph(num_nodes):
    graph = nx.Graph()
    graph.add_nodes_from(range(num_nodes))
    for proc in range(num_nodes):
        graph.add_edge(proc, (proc + 1) % num_nodes)
    return graph

def generate_grid_graph(num_nodes):
    grid_dim = int(math.sqrt(num_nodes))
    graph = nx.Graph()
    graph.add_nodes_from(range(num_nodes))
    for row in range(grid_dim):
        for col in range(grid_dim):
            curr_node = row * grid_dim + col
            if col + 1 < grid_dim:
                graph.add_edge(curr_node, row * grid_dim + (col + 1))
            if row + 1 < grid_dim:
                graph.add_edge(curr_node, (row + 1) * grid_dim + col)
    return graph

def generate_cube_graph(dimensions):
    num_nodes = 2 ** dimensions
    graph = nx.Graph()
    graph.add_nodes_from(range(num_nodes))
    for i in range(num_nodes):
        for b in range(dimensions):
            adj = i ^ (1 << b)
            if adj > i:
                graph.add_edge(i, adj)
    return graph

def plot_all_topologies(nodes, dims):
    fig, axs = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(f"Network Topologies for N = {nodes}", fontsize=15, fontweight='bold', color='darkblue')

    # Ring
    ring_g = generate_ring_graph(nodes)
    ring_pos = {i: (math.cos(2*math.pi*i/nodes), math.sin(2*math.pi*i/nodes)) for i in range(nodes)}
    axs[0].set_title("Ring Network")
    nx.draw(ring_g, ring_pos, ax=axs[0], node_color='crimson', node_size=400, edge_color='gray', with_labels=True, font_color='white')

    # Grid
    grid_g = generate_grid_graph(nodes)
    side = int(math.sqrt(nodes))
    grid_pos = {r * side + c: (c, -r) for r in range(side) for c in range(side)}
    axs[1].set_title("2D Grid Network")
    nx.draw(grid_g, grid_pos, ax=axs[1], node_color='purple', node_size=400, edge_color='gray', with_labels=True, font_color='white')

    # Cube
    cube_g = generate_cube_graph(dims)
    cube_pos = nx.spring_layout(cube_g, seed=24)
    axs[2].set_title("Hypercube Network")
    nx.draw(cube_g, cube_pos, ax=axs[2], node_color='teal', node_size=400, edge_color='gray', with_labels=True, font_color='white')

    plt.savefig("z_topologies_plot.png", dpi=100)
    plt.close()

# =====================================================================
# 2. Algorithm Simulators
# =====================================================================

class RingCommSimulator:
    def __init__(self, n_procs):
        self.n = n_procs
        self.total_steps = 0
        self.send_buffers = {i: {j: (i, j) for j in range(n_procs) if i != j} for i in range(n_procs)}
        self.inbox = {i: [] for i in range(n_procs)}

    def run_all_to_all(self):
        t_start = time.perf_counter()
        for idx in range(1, self.n):
            for proc in range(self.n):
                target = (proc + idx) % self.n
                if target in self.send_buffers[proc]:
                    self.inbox[target].append(self.send_buffers[proc][target])
            self.total_steps += 1
        return time.perf_counter() - t_start

class MeshCommSimulator:
    def __init__(self, n_procs):
        self.n = n_procs
        self.dim = int(math.sqrt(n_procs))
        self.total_steps = 0
        self.send_buffers = {i: {j: (i, j) for j in range(n_procs) if i != j} for i in range(n_procs)}
        self.inbox = {i: [] for i in range(n_procs)}

    def get_id(self, r, c):
        return r * self.dim + c

    def run_all_to_all(self):
        t_start = time.perf_counter()
        temp_storage = {i: {} for i in range(self.n)}

        # Row Exchange
        for r in range(self.dim):
            r_procs = [self.get_id(r, c) for c in range(self.dim)]
            for sender in r_procs:
                for dest_proc, packet in self.send_buffers[sender].items():
                    dest_c = dest_proc % self.dim
                    relay = self.get_id(r, dest_c)
                    temp_storage[relay][dest_proc] = packet
        self.total_steps += (self.dim - 1)

        # Col Exchange
        for c in range(self.dim):
            c_procs = [self.get_id(r, c) for r in range(self.dim)]
            for relay in c_procs:
                for dest_proc, packet in temp_storage[relay].items():
                    self.inbox[dest_proc].append(packet)
        self.total_steps += (self.dim - 1)
        return time.perf_counter() - t_start

class HypercubeCommSimulator:
    def __init__(self, n_procs):
        self.n = n_procs
        self.d = int(math.log2(n_procs))
        self.total_steps = 0
        self.packets = {i: {j: (i, j) for j in range(n_procs)} for i in range(n_procs)}
        self.inbox = {i: [] for i in range(n_procs)}

    def run_all_to_all(self):
        t_start = time.perf_counter()
        current_data = self.packets

        for dim_idx in range(self.d):
            next_data = {i: {} for i in range(self.n)}
            bitmask = (1 << (dim_idx + 1)) - 1
            for p in range(self.n):
                neighbor = p ^ (1 << dim_idx)
                for dst, pkt in current_data[p].items():
                    if (dst & bitmask) == (p & bitmask):
                        next_data[p][dst] = pkt
                    else:
                        next_data[neighbor][dst] = pkt
            current_data = next_data
            self.total_steps += 1

        for p in range(self.n):
            for dst, pkt in current_data[p].items():
                if pkt[0] != pkt[1]: # Ignore self-loops
                    self.inbox[p].append(pkt)
        
        return time.perf_counter() - t_start

def check_correctness(inbox_data, procs):
    for proc_id in range(procs):
        messages = inbox_data[proc_id]
        if len(messages) != (procs - 1):
            return False
        for m in messages:
            if m[1] != proc_id:
                return False
    return True

# =====================================================================
# Main Execution Sequence
# =====================================================================

if __name__ == '__main__':
    node_configs = [4, 16, 64]
    
    print("--- PDC A2 Q1 - Zeenat Ijaz (23F-0054) ---")
    plot_all_topologies(16, 4)
    print("Topologies plotted successfully.")
    
    results = []
    for num_nodes in node_configs:
        r_sim = RingCommSimulator(num_nodes)
        t_r = r_sim.run_all_to_all()
        check_correctness(r_sim.inbox, num_nodes)
        
        m_sim = MeshCommSimulator(num_nodes)
        t_m = m_sim.run_all_to_all()
        check_correctness(m_sim.inbox, num_nodes)
        
        h_sim = HypercubeCommSimulator(num_nodes)
        t_h = h_sim.run_all_to_all()
        check_correctness(h_sim.inbox, num_nodes)
        
        results.append((num_nodes, r_sim.total_steps, m_sim.total_steps, h_sim.total_steps, t_r, t_m, t_h))
        
    print("\n[ Performance Metrics ]")
    print(f"{'Nodes':<6} | {'Ring(Steps)':<12} | {'Mesh(Steps)':<12} | {'Cube(Steps)':<12} | {'Ring(Time)':<12} | {'Mesh(Time)':<12} | {'Cube(Time)':<12}")
    for res in results:
        print(f"{res[0]:<6} | {res[1]:<12} | {res[2]:<12} | {res[3]:<12} | {res[4]:.6f}     | {res[5]:.6f}     | {res[6]:.6f}")

