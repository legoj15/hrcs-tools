import os
import re

# Define the entries and their replacement values
entries = {
    "fademaxdist": "0",
    "fademindist": "-1",
    "PerformanceMode": "2"
}

# Initialize a dictionary to keep count of replacements
counts = {
    "fademaxdist": 0,
    "fademindist": 0,
    "PerformanceMode": 0
}

# Initialize a variable to store the smallest lightmapscale value
smallest_lightmapscale = float('inf')

# Get a list of all .vmf files in the current directory
files = [f for f in os.listdir() if f.endswith('.vmf')]

# Iterate over each file
for file in files:
    with open(file, 'r') as f:
        content = f.read()

    # Iterate over each entry
    for entry, replacement in entries.items():
        # Create a regex pattern for the entry
        pattern = r'\"{}\" \"\d+\"'.format(entry)

        # Find all matches in the content
        matches = re.findall(pattern, content)

        # Replace all matches with the replacement value
        content = re.sub(pattern, '\"{}\" \"{}\"'.format(entry, replacement), content)

        # Update the count for this entry
        counts[entry] += len(matches)

    # Find all lightmapscale values
    lightmapscale_values = re.findall(r'\"lightmapscale\" \"(\d+)\"', content)

    # Update the smallest lightmapscale value
    for value in lightmapscale_values:
        smallest_lightmapscale = min(smallest_lightmapscale, int(value))

    # Write the updated content back to the file
    with open(file, 'w') as f:
        f.write(content)

# Print the counts
for entry, count in counts.items():
    print('Replaced {} instances of "{}".'.format(count, entry))

# Print the smallest lightmapscale value
print('The smallest "lightmapscale" value is {}.'.format(smallest_lightmapscale))
