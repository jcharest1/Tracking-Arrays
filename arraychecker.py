# Import required libraries
import pandas as pd
import numpy as np
import csv
import os

# Define a function that calculates the vector between two points in 3D space
def get_vector(a, b):
    return b - a

# Define a function that calculates the length of a vector
def get_length(v):
    return np.linalg.norm(v)

# Define a function that calculates the angle between two vectors
def get_angle(v1, v2):
    return np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

# Define a function to perform checks on segments lengths
def check_segments(segments):
    for seg, length in segments.items():
        # Check if a segment is less than 50mm
        if length < 50:
            return False, f"segment {seg} is less than 50mm"
        for seg2, length2 in segments.items():
            # Check if the difference between two segments is < 3.5
            if seg != seg2 and abs(length - length2) < 3.5:
                return False, f"segment {seg} and segment {seg2} are within {abs(length - length2)} mm of one another"
    return True, ""

# Read input data from CSV
data = pd.read_csv("marker_geometries.csv")

new_data = []  # An empty list to store the new data
all_angles = []  # An empty list to store all angles

# Iterate over each row in the dataframe
for i, row in data.iterrows():
    # Extract coordinates for each point in the array and store as a dictionary of numpy arrays
    points = {name: np.array([row[f'Point{name}_x'], row[f'Point{name}_y'], row[f'Point{name}_z']]) for name in ['A', 'B', 'C', 'D']}
    # Calculate vectors (segments) between points and store as a dictionary
    segments = {f"{name1}{name2}": get_vector(points[name1], points[name2]) for name1 in ['A', 'B', 'C', 'D'] for name2 in ['B', 'C', 'D'] if name1 < name2}
    # Calculate lengths of each segment and store as a dictionary
    lengths = {seg: get_length(vec) for seg, vec in segments.items()}
    # Calculate angles between segments and store as a dictionary
    angles = {f"{seg1}-{seg2}": [lengths[seg1], lengths[seg2], get_angle(segments[seg1], segments[seg2])] for seg1 in lengths for seg2 in lengths if seg1 < seg2}

    # Check if any segment fails the checks defined earlier
    status, reason = check_segments(lengths)
    if status:
        for idx, prev_angles in enumerate(all_angles):
            for angle_name, angle in angles.items():
                for prev_angle_name, prev_angle in prev_angles.items():
                    # Compare each segment pair angle of one array to all of the segment pair angles of all other arrays
                    if abs(angle[0] - prev_angle[0]) <= 3.5 and abs(angle[1] - prev_angle[1]) <= 3.5 and abs(angle[2] - prev_angle[2]) <= 0.0349066:
                        status = False
                        reason = f"Segment pair {angle_name} is similar to segment pair {prev_angle_name} in {new_data[idx][0]}"
                        break
                if not status:
                    break
            if not status:
                break

    # Append the current angles to the list of all angles
    all_angles.append(angles)
    # Create a new row and append it to the new data
    new_row = [row['ArrayName']] + [coord for name in ['A', 'B', 'C', 'D'] for coord in points[name]] + [status, reason] + [length for length in lengths.values()] + [str(angles[val]) for val in angles.keys()]
    new_data.append(new_row)

# Define the headers for the new data
headers = ['ArrayName'] + [f'Point{name}_{coord}' for name in ['A', 'B', 'C', 'D'] for coord in ['x', 'y', 'z']] + ['Check Status', 'Failure Reason'] + [f'Segment {name}' for name in ['AB', 'AC', 'AD', 'BC', 'BD', 'CD']] + [f'Segment Pair {name1} Data' for name1 in ['AB-AC', 'AB-AD', 'AB-BC', 'AB-BD', 'AB-CD', 'AC-AD', 'AC-BC', 'AC-BD', 'AC-CD', 'AD-BC', 'AD-BD', 'AD-CD', 'BC-BD', 'BC-CD', 'BD-CD']]

# Write the new data to a CSV file
with open('marker_geometries_checked.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(new_data)

# Open the results file
os.startfile('marker_geometries_checked.csv')