import numpy as np
from collections import deque

def grid_to_adjacency_matrix(N):
    """
    Converts a grid of size N x N into an adjacency matrix representing connections between neighboring nodes.
    
    Args:
    - N (int): The size of the grid (N x N).
    
    Returns:
    - adj_matrix (numpy.ndarray): The adjacency matrix representing the graph.
    """
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
    """
    Perform BFS from the start node to the end node and return the edges used,
    given an adjacency matrix representation of the graph.
    
    Args:
    - adj_matrix (numpy.ndarray): The adjacency matrix of the graph.
    - start (tuple): Starting node (r, c) tuple, e.g., (0, 0).
    - end (tuple): Ending node (r, c) tuple, e.g., (3, 3).
    - N (int): Size of the grid (N x N).
    
    Returns:
    - path_edges (list): List of edges used to reach the target node from the start.
    """
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

# Example Usage:
N = 4  # Define grid size (e.g., 4x4 grid)
adj_matrix = grid_to_adjacency_matrix(N)

# Define start and end nodes
start_node = (0, 0)  # Starting node
end_node = (3, 3)  # Ending node

# Perform BFS and get the edges used to reach the target
edges_used = bfs_with_edges_from_matrix(adj_matrix, start_node, end_node, N)

# Print the result (now it's cleaner)
print("Edges used to reach the target node:")
for edge in edges_used:
    print(edge)

