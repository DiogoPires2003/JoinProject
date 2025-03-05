import sys
import requests
import pandas as pd
import matplotlib.pyplot as plt

# GitHub repository details (replace with actual repo)
repo = 'DiogoPires2003/JoinProject'  # Replace with your organization/repository
token = 'your-github-token'  # This will be passed from GitHub secrets in the workflow

# Fetch issue numbers passed as arguments
issue_numbers = sys.argv[1].split()  # Expecting space-separated issue numbers

# Conventional commit patterns to filter issues by
commit_patterns = ['feat:', 'fix:', 'docs:', 'chore:', 'style:', 'refactor:', 'test:']

# List to store filtered issue data
filtered_issues = []

# Fetch data for each issue
for issue_number in issue_numbers:
    url = f'https://api.github.com/repos/{repo}/issues/{issue_number}'
    response = requests.get(url, headers={'Authorization': f'token {token}'})
    
    if response.status_code == 200:
        issue = response.json()
        
        # Check if the issue title matches any of the conventional commit patterns
        if any(issue['title'].lower().startswith(pattern) for pattern in commit_patterns):
            filtered_issues.append({
                'Issue Type': issue['title'],
                'Count': 1,  # We will assume each filtered issue has a count of 1
                'Severity': issue.get('labels', [{'name': 'Unknown'}])[0]['name']  # Use the first label as severity
            })

# If no issues match, exit the script
if not filtered_issues:
    print("No issues found with conventional commits.")
    sys.exit()

# Convert to DataFrame
df = pd.DataFrame(filtered_issues)

# If no issues with the conventional commits are found, exit
if df.empty:
    print("No issues found matching conventional commit types.")
    sys.exit()

# Sort data in descending order of frequency (count)
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

print("Pareto chart saved as 'pareto_chart.png'.")
