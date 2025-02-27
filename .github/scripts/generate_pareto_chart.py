import matplotlib.pyplot as plt
from collections import Counter
import requests

# Get issues from the GitHub API
response = requests.get('https://api.github.com/repos/DiogoPires2003/JoinProject/issues?state=all')
issues = response.json()

# Count the occurrences of each label
label_counts = Counter(label['name'] for issue in issues for label in issue['labels'])

# Sort labels by count in descending order
sorted_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
labels, counts = zip(*sorted_labels)

# Create the Pareto chart
fig, ax = plt.subplots()
ax.bar(labels, counts, color='b')
ax.set_xlabel('Labels')
ax.set_ylabel('Number of Issues')
ax.set_title('Pareto Chart of Issues by Label')

# Plot cumulative percentage line
cumulative_counts = [sum(counts[:i+1]) for i in range(len(counts))]
cumulative_percentage = [count / cumulative_counts[-1] * 100 for count in cumulative_counts]
ax2 = ax.twinx()
ax2.plot(labels, cumulative_percentage, color='r', marker='D', ms=5)
ax2.set_ylabel('Cumulative Percentage')

# Save the chart
plt.savefig('pareto_chart.png')
