import os
import re
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

# Regular expression for conventional commit format
conventional_commit_regex = r'^(feat|fix|chore|docs|style|refactor|test)(\([^\)]+\))?: .+'

# Fetch issues from the repository
response = requests.get(url, headers=headers)

# Check for valid response
if response.status_code != 200:
    print(f"Error fetching issues: {response.status_code} - {response.text}")
    exit(1)

issues = response.json()

# Process the issue data
data = {'Issue Type': [], 'Count': [], 'Severity': []}

for issue in issues:
    if isinstance(issue, dict) and 'pull_request' not in issue:  # Exclude pull requests and ensure it's a valid issue
        # Check if issue has any commits (via associated PR commits or other)
        commits_url = issue.get('comments_url', '').replace('comments', 'commits')
        
        if commits_url:
            commits_response = requests.get(commits_url, headers=headers)
            if commits_response.status_code != 200:
                print(f"Error fetching commits: {commits_response.status_code} - {commits_response.text}")
                continue  # Skip this issue if there's an error fetching commits
            
            commits = commits_response.json()
            
            # Check each commit message against the conventional commit regex
            for commit in commits:
                commit_message = commit.get('commit', {}).get('message', '')
                if re.match(conventional_commit_regex, commit_message):
                    # If the commit follows conventional commit format, process this issue
                    labels = issue.get('labels', [])
                    if labels:  # If there are labels, use the first one
                        issue_type = labels[0].get('name', 'Unlabeled')
                    else:
                        issue_type = 'Unlabeled'  # No labels found
                    severity = 'High'  # You can customize how to map severity from issue labels or other properties
                    data['Issue Type'].append(issue_type)
                    data['Count'].append(1)
                    data['Severity'].append(severity)
                    break  # Stop after finding the first valid conventional commit

# Create a DataFrame
df = pd.DataFrame(data)

# If no data was added, print a message
if df.empty:
    print("No issues with conventional commits found.")
    exit(0)

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
