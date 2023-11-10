# dradis.py
import os

def aggregate_results(output_dir):
    results = []

    # Iterate through files in the output directory
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)

        # Read and append content of each file to the results list
        with open(filepath, 'r') as file:
            results.append(file.read())

    # Perform additional processing or analysis as needed
    # For now, join the results into a single string
    aggregated_results = '\n'.join(results)

    return aggregated_results
