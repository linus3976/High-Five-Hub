import numpy as np
from collections import deque

def grid_to_adjacency_matrix(N):
    # Initialize an empty adjacency matrix (N*N x N*N)
    adj_matrix = np.zeros((N*N, N*N), dtype=int)
    
    # Function to convert grid coordinates (r, c) to matrix index
    def node_to_index(r, c):
        return r * N + c
    
    for r in range(N):
        for c in range(N):
            current_node = node_to_index(r, c)
            
            # Connect to the right and bottom neighbors if within bounds
            if c + 1 < N:  # Right neighbor
                right_node = node_to_index(r, c + 1)
                adj_matrix[current_node][right_node] = 1
                adj_matrix[right_node][current_node] = 1  # Undirected graph
                
            if r + 1 < N:  # Bottom neighbor
                bottom_node = node_to_index(r + 1, c)
                adj_matrix[current_node][bottom_node] = 1
                adj_matrix[bottom_node][current_node] = 1  # Undirected graph
                
    return adj_matrix


def bfs_with_edges_from_matrix(adj_matrix, start, end, N):
    # Map grid coordinates to matrix indices
    def node_to_index(r, c):
        return r * N + c

    # Convert start and end coordinates to matrix indices
    start_index = node_to_index(*start)
    end_index = node_to_index(*end)
    
    # Queue for BFS and visited set to track visited nodes
    queue = deque([start_index])
    visited = set([start_index])
    
    # Dictionary to store the parent of each node (used for backtracking the path)
    parent = {start_index: None}
    
    # List to store the edges used
    path_edges = []
    
    while queue:
        current_node = queue.popleft()
        
        # If we reach the target node, backtrack the path
        if current_node == end_index:
            # Backtrack the path using the parent dictionary
            path_node = end_index
            while parent[path_node] is not None:
                prev_node = parent[path_node]
                prev_r, prev_c = divmod(prev_node, N)
                curr_r, curr_c = divmod(path_node, N)
                # Append edges as tuples of grid coordinates (not np.int64)
                path_edges.append(((int(prev_r), int(prev_c)), (int(curr_r), int(curr_c))))  
                path_node = prev_node
            path_edges.reverse()  # Reverse the list to get the correct order
            return path_edges
        
        # Explore neighbors by checking the adjacency matrix (using NumPy slicing)
        neighbors = np.where(adj_matrix[current_node] == 1)[0]
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current_node  # Set the parent of the neighbor
                queue.append(neighbor)
    
    return []  # Return an empty list if no path found

"""
(1, 0) for right
(-1, 0) for left
(0, 1) for up
(0, -1) for down
"""

#/!\ DO NOT MAKE IT START IN THE OPPOSITE DIRECTION IT'S SUPPOSED TO GO! (ie, putting it facing a white line will always do the trick)

#We might want to implement this as a method in hindsight...
def dir_list_absolute(edge_list):
    l = []

    for i in range (len(edge_list)):
        l.append(tuple(b - a for a, b in zip(edge_list[i][0], edge_list[i][1])))
    return l

def dir_list(dir_l, og_dir):
    # Define possible directions
    directions = {
        (1, 0): "right",
        (-1, 0): "left",
        (0, 1): "up",
        (0, -1): "down"
    }
    
    # Define relative direction changes based on the current orientation
    turns = {
        "up": {"up": "straight", "right": "right", "left": "left"},
        "down": {"down": "straight", "right": "left", "left": "right"},
        "right": {"right": "straight", "up": "left", "down": "right"},
        "left": {"left": "straight", "up": "right", "down": "left"},
    }
    
    # Convert og_dir tuple to string if necessary
    if isinstance(og_dir, tuple):
        og_dir = directions.get(og_dir)
    
    # Ensure og_dir is now a valid string direction
    if og_dir not in turns:
        raise ValueError(f"Invalid initial direction: {og_dir}")

    # Start with the initial facing direction
    current_dir = og_dir
    relative_directions = []

    for move in dir_l:
        # Get the absolute direction as a string (e.g., "right", "up")
        abs_dir = directions.get(move)
        if abs_dir is None:
            raise ValueError(f"Invalid move direction: {move}")

        # Determine the relative direction
        relative_dir = turns[current_dir][abs_dir]
        relative_directions.append(relative_dir)
        
        # Update the current direction to the new absolute direction
        current_dir = abs_dir
    
    return relative_directions


















# Example Usage:
N = 4  # Define grid size (e.g., 4x4 grid)
adj_matrix = grid_to_adjacency_matrix(N)

# Define start and end nodes
start_node = (3, 3)  # Starting node
end_node = (0, 0)  # Ending node

# Perform BFS and get the edges used to reach the target
edges_used = bfs_with_edges_from_matrix(adj_matrix, start_node, end_node, N)

# Print the result (now it's cleaner)
print("Edges used to reach the target node:")
for edge in edges_used:
    print(edge)

#test de dir_list
dir = dir_list_absolute(edges_used)
print("list of directions :")
for d in dir:
    print(d)
dir_rel = dir_list(dir, (1,0))
print("list of relative directins : ")
for d in dir_rel:
    print(d)
