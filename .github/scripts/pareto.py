import pandas as pd
import matplotlib.pyplot as plt

# Sample data: replace with actual issue data
data = {
    'Issue Type': ['UI Bug', 'Crash', 'Performance Issue', 'Security Vulnerability', 'API Error'],
    'Count': [150, 80, 60, 30, 20],
    'Severity': ['High', 'Critical', 'Medium', 'High', 'Low']
}
df = pd.DataFrame(data)

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
