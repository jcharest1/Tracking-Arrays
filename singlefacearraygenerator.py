import csv
import math
import numpy as np
from scipy.spatial import distance
import os

# Define the number of arrays and constraints for each array
num_arrays = 2

base_name = 'Gen Array'  # Base name for the set of arrays this is generating

# Define constraints for each point in the arrays
constraints_list_1 = [
    # Point A
    {
        'min_x': -50, 'max_x': -10, 'min_y': 30, 'max_y': 100, 
        'z_func': lambda x, y: 0
    },
    # Point B
    {
        'min_x': 10, 'max_x': 50, 'min_y': 30, 'max_y': 100, 
        'z_func': lambda x, y: 0
    },
    # Point C
    {
        'min_x': 10, 'max_x': 50, 'min_y': -30, 'max_y': -100, 
        'z_func': lambda x, y: 0
    },
    # Point D
    {
        'min_x': -50, 'max_x': -10, 'min_y': -30, 'max_y': -100, 
        'z_func': lambda x, y: 0
    }
]

def vector_length(a, b):
    """Computes vector and Euclidean distance between points a and b."""
    return np.array(a) - np.array(b), distance.euclidean(a, b)

def angle_between(a, b):
    """Computes angle in radians between vectors a and b."""
    return np.arccos(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def calculate_segments(points):
    """Computes lengths of all possible segments between given points."""
    return [(vector_length(points[i], points[j])[1], vector_length(points[i], points[j])[0], i, j) for i in range(len(points)) for j in range(i+1, len(points))]

def calculate_segment_pairs(segments):
    """Computes lengths and angle for all possible pairs of segments."""
    return [(segments[i][0], segments[j][0], angle_between(segments[i][1], segments[j][1])) for i in range(len(segments)) for j in range(i+1, len(segments))]

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
    for i, (length1, vector1, point1, point2) in enumerate(segments):
        if length1 < 50 or any(abs(length1 - length2) < 3.5 for length2, vector2, _, _ in segments[i+1:]):
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
                writer.writerow([f"{base_name} {i+1}"] + list(np.array(points).flatten()))
            existing_segment_pairs.extend(segment_pairs)
            print(points)
            break

            break  # If successful, break the loop


    os.startfile('marker_geometries.csv')

if __name__ == "__main__":
    main()
