"""
----------------------------------------------------------------------
PDC Assignment 2 - Section B, Question 2
Circular Shift on Toroidal Mesh
Student Name: Zeenat Ijaz
Roll Number : 23F-0054
Section     : AI-6A
----------------------------------------------------------------------
"""

import threading
import time
import math
import numpy as np
import matplotlib.pyplot as plt

class ZeenatMeshShift:
    def __init__(self, total_nodes, shift_amount):
        self.P = total_nodes
        self.grid_dim = int(math.sqrt(total_nodes))
        self.q = shift_amount
        
        self.data_grid = [[row * self.grid_dim + col for col in range(self.grid_dim)] for row in range(self.grid_dim)]
        self.temp_grid = [[0] * self.grid_dim for _ in range(self.grid_dim)]
        
        self.phase1_barrier = threading.Barrier(self.P)
        self.phase2_barrier = threading.Barrier(self.P)
        self.threads = []

    def log_state(self, phase):
        print(f"\n--- {phase} ---")
        for row in self.data_grid:
            print(" ".join(f"{item:4d}" for item in row))
            
    def worker_logic(self, r, c):
        my_val = self.data_grid[r][c]
        row_shift = self.q % self.grid_dim
        col_shift = self.q // self.grid_dim
        
        # Row shift phase
        new_c = (c + row_shift) % self.grid_dim
        self.temp_grid[r][new_c] = my_val
        self.phase1_barrier.wait()
        
        if c == 0: # single thread per row writes back
            self.data_grid[r] = list(self.temp_grid[r])
        self.phase1_barrier.wait()
        
        # Col shift phase
        current_val = self.data_grid[r][c]
        new_r = (r + col_shift) % self.grid_dim
        self.temp_grid[new_r][c] = current_val
        self.phase2_barrier.wait()

        if r == 0:
            for rw in range(self.grid_dim):
                self.data_grid[rw][c] = self.temp_grid[rw][c]
        self.phase2_barrier.wait()

    def run_simulation(self):
        self.log_state("Initial Grid")
        
        t_start = time.perf_counter()
        
        for r in range(self.grid_dim):
            for c in range(self.grid_dim):
                t = threading.Thread(target=self.worker_logic, args=(r, c))
                self.threads.append(t)
                t.start()
                
        for t in self.threads:
            t.join()
            
        t_end = time.perf_counter()
        
        self.log_state(f"Final Grid after q={self.q} shift")
        return t_end - t_start

if __name__ == '__main__':
    print("Mesh Circular Shift Simulator - Zeenat (23F-0054)")
    sim = ZeenatMeshShift(total_nodes=16, shift_amount=5)
    t = sim.run_simulation()
    print(f"\nExecution time: {t:.5f}s")
