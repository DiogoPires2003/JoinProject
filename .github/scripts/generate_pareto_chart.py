import requests
import matplotlib.pyplot as plt

# Replace with your repository owner and name
owner = "DiogoPires2003"
repo = "JoinProject"

# Fetch open issues
open_issues = requests.get(f"https://api.github.com/repos/{owner}/{repo}/issues?state=open").json()
# Fetch closed issues
closed_issues = requests.get(f"https://api.github.com/repos/{owner}/{repo}/issues?state=closed").json()

# Count issues by labels
issue_counts = {}
for issue in open_issues + closed_issues:
    for label in issue.get('labels', []):
        label_name = label['name']
        issue_counts[label_name] = issue_counts.get(label_name, 0) + 1

# Sort issues by count
sorted_issue_counts = dict(sorted(issue_counts.items(), key=lambda item: item[1], reverse=True))

# Generate Pareto Diagram
labels = list(sorted_issue_counts.keys())
counts = list(sorted_issue_counts.values())

plt.figure(figsize=(10, 6))
plt.bar(labels, counts, color='blue')
plt.xlabel('Issue Labels')
plt.ylabel('Number of Issues')
plt.title('Pareto Diagram of Issues')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('pareto_diagram.png')
