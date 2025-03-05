import os
import requests
import pandas as pd
import matplotlib.pyplot as plt

# GitHub repository details
repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER')  # This will be set automatically by GitHub Actions
repo_name = os.getenv('GITHUB_REPOSITORY').split('/')[1]
github_token = os.getenv('GH_PAT')  # Make sure you set this secret in your GitHub Actions

# GitHub API endpoint for issues
url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"

# Set up the headers with authentication
headers = {
    "Authorization": f"token {github_token}"
}

# Fetch issues from the repository
response = requests.get(url, headers=headers)
issues = response.json()

# Process the issue data
data = {'Issue Type': [], 'Count': [], 'Severity': []}

for issue in issues:
    if 'pull_request' not in issue:  # Exclude pull requests
        issue_type = issue.get('labels', [{}])[0].get('name', 'Unlabeled')  # Use the first label as the issue type
        severity = 'High'  # You can customize how to map severity from issue labels or other properties
        data['Issue Type'].append(issue_type)
        data['Count'].append(1)
        data['Severity'].append(severity)

# Create a DataFrame
df = pd.DataFrame(data)

# Group by issue type and count occurrences
df = df.groupby(['Issue Type']).agg({'Count': 'sum'}).reset_index()

# Sort data in descending order of frequency
df = df.sort_values(by='Count', ascending=False)

# Calculate cumulative percentage for Pareto chart
df['Cumulative Percentage'] = df['Count'].cumsum() / df['Count'].sum() * 100

# Plot the Pareto chart
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart for frequency count
ax1.bar(df['Issue Type'], df['Count'], color='b', label='Frequency')
ax1.set_ylabel('Frequency', color='b')
ax1.set_xlabel('Issue Type')
ax1.tick_params(axis='y', labelcolor='b')

# Line chart for cumulative percentage
ax2 = ax1.twinx()
ax2.plot(df['Issue Type'], df['Cumulative Percentage'], color='r', marker='o', linestyle='-', label='Cumulative %')
ax2.set_ylabel('Cumulative Percentage', color='r')
ax2.tick_params(axis='y', labelcolor='r')

plt.title('Pareto Chart of Issues')
plt.xticks(rotation=45)
plt.grid(True)

# Save the plot to a file
plt.savefig('pareto_chart.png', bbox_inches='tight')
