import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime

# Get issues data from file
issues_file = os.getenv('ISSUES_FILE')
with open(issues_file, 'r') as file:
    issues_data = file.read()

issues = json.loads(issues_data)
print("Total issues fetched:", len(issues))

# Extract labels from issues
labels = []
for issue in issues:
    issue_labels = issue.get('labels', [])
    for label in issue_labels:
        labels.append(label['name'])

print("Labels:", labels)

# Count frequency of each label
label_counts = pd.Series(labels).value_counts().reset_index()
label_counts.columns = ['Label', 'Count']
print("Label counts:", label_counts)

# Sort data in descending order of frequency
label_counts = label_counts.sort_values(by='Count', ascending=False)

# Calculate cumulative percentage for histogram
label_counts['Cumulative Percentage'] = label_counts['Count'].cumsum() / label_counts['Count'].sum() * 100

# Plot the histogram
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart for frequency count
ax1.bar(label_counts['Label'], label_counts['Count'], color='b', label='Frequency')
ax1.set_ylabel('Frequency', color='b')
ax1.set_xlabel('Label')
ax1.tick_params(axis='y', labelcolor='b')

# Save the plot to a file
file_name = "histogram.png"
plt.savefig(file_name, bbox_inches='tight')
plt.show()
