import csv
import math
import numpy as np
from scipy.spatial import distance
import os

# Define the number of arrays and constraints for each array
num_arrays = 4

base_name = 'Gen Two Face Array'  # Base name for the set of arrays this is generating

# Define constraints for each point in top face arrays
constraints_list_1 = [
    # Point A
    {
        'min_x': -50, 'max_x': -10, 'min_y': 30, 'max_y': 100, 
        'z_func': lambda x, y: -y / np.tan(np.radians(60)) + 5.18 # points lie on a 60 deg plane that is a function of y
    },
    # Point B
    {
        'min_x': 10, 'max_x': 50, 'min_y': 30, 'max_y': 100, 
        'z_func': lambda x, y: -y / np.tan(np.radians(60)) + 5.18 # points lie on a 60 deg plane that is a function of y
    },
    # Point C
    {
        'min_x': 10, 'max_x': 50, 'min_y': 0, 'max_y': 0, 
        'z_func': lambda x, y: 6
    },
    # Point D
    {
        'min_x': -50, 'max_x': -10, 'min_y': 0, 'max_y': 0, 
        'z_func': lambda x, y: 6
    }
]

# Define constraints for each point in bottom face arrays
constraints_list_2 = [
    # Point A - defined in main()
        # New Point A is old Point D

    #Point B - defined in main()
        # New Point B is old Point C

    # Point C
    {
        'min_x': 10, 'max_x': 50, 'min_y': -100, 'max_y': -30, 
        'z_func': lambda x, y: -y / np.tan(np.radians(-60))-5.18
    },
    
    # Point D
    {
        'min_x': -50, 'max_x': -10, 'min_y': -100, 'max_y': -30, 
        'z_func': lambda x, y: -y / np.tan(np.radians(-60))-5.18
    }
]

def vector_length(a, b):
    """Computes Euclidean distance between points a and b."""
    return distance.euclidean(a, b)

def angle_between(a, b):
    """Computes angle in radians between vectors a and b."""
    return np.arccos(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def calculate_segments(points):
    """Computes lengths of all possible segments between given points."""
    return [(vector_length(points[i], points[j]), i, j) for i in range(len(points)) for j in range(i+1, len(points))]

def calculate_segment_pairs(segments):
    """Computes lengths and angle for all possible pairs of segments."""
    return [(segments[i][0], segments[j][0], angle_between(segments[i], segments[j])) for i in range(len(segments)) for j in range(i+1, len(segments))]

def random_point(min_x=None, max_x=None, min_y=None, max_y=None, z_func=None, point=None):
    """Generates a random point in 3D space given constraints."""
    if point is not None:
        return point
    x = round(np.random.uniform(min_x, max_x), 1)  # Random x within bounds rounded to nearest 0.1
    y = round(np.random.uniform(min_y, max_y), 1)  # Random y within bounds rounded to nearest 0.1
    z = z_func(x, y)  # Computes z using provided function
    return np.array([x, y, z])  # Returns 3D point as a NumPy array


def generate_points(constraints):
    """Generates a list of points given constraints."""
    return [random_point(**con) for con in constraints]

def check_segments(segments):
    """Checks if any segment is shorter than 50 or difference between any two segments is less than 3.5."""
    for i, (length1, _, _) in enumerate(segments):
        if length1 < 50 or any(abs(length1 - length2) < 3.5 for length2, _, _ in segments[i+1:]):
            return False
    return True

def check_segment_pairs(segment_pairs, existing_segment_pairs):
    """Checks if any pair of segments matches any existing pair of segments within certain tolerances."""
    for length1, length2, angle in segment_pairs:
        if any(abs(length1 - ex_length1) <= 3.5 and abs(length2 - ex_length2) <= 3.5 and abs(angle - ex_angle) <= 0.0349066 for ex_length1, ex_length2, ex_angle in existing_segment_pairs):
            return False
    return True

def main():
    # Load existing segment pairs from file
    with open('marker_geometries.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  
        existing_segment_pairs = [pair for row in reader for pair in calculate_segment_pairs(calculate_segments(np.array([list(map(float, row[i:i+3])) for i in range(1, 13, 3)], dtype=float)))]

    for i in range(num_arrays):
        while True:
            # Generate points and calculate segments and pairs
            points = generate_points(constraints_list_1)
            segments = calculate_segments(points)
            segment_pairs = calculate_segment_pairs(segments)
            
            # Check if generated segments and pairs satisfy conditions
            if not check_segments(segments) or not check_segment_pairs(segment_pairs, existing_segment_pairs):
                continue
            
            # Write to file if conditions are satisfied
            with open('marker_geometries.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f"{base_name} {i+1}" + ' - Top'] + list(np.array(points).flatten()))
            existing_segment_pairs.extend(segment_pairs)
            print(points)
            break

        while True:
            # Generate points and calculate segments and pairs for bottom face
            new_constraints = [
                {'point': points[3]}, # New Point A is the old Point D
                {'point': points[2]} # New Point B is the old Point C
            ]
            new_constraints.extend(constraints_list_2)
            points2 = generate_points(new_constraints)
            segments2 = calculate_segments(points2)
            if not check_segments(segments2):
                continue
            segment_pairs2 = calculate_segment_pairs(segments2)
            if not check_segment_pairs(segment_pairs2, existing_segment_pairs):
                continue

            # Write to file if conditions are satisfied
            with open('marker_geometries.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f"{base_name} {i+1}" + ' - Bottom'] + list(np.array(points2).flatten()))
            existing_segment_pairs.extend(segment_pairs2)
            print(points2)
            break
            

            break  # If successful, break the loop


    os.startfile('marker_geometries.csv')

if __name__ == "__main__":
    main()
