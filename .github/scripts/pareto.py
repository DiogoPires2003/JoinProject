import pandas as pd
import matplotlib.pyplot as plt

# Sample data: replace with actual data source
data = {
    'Category': ['Defect A', 'Defect B', 'Defect C', 'Defect D', 'Defect E'],
    'Count': [50, 30, 15, 10, 5]
}
df = pd.DataFrame(data)

# Sort data in descending order
df = df.sort_values(by='Count', ascending=False)

df['Cumulative Percentage'] = df['Count'].cumsum() / df['Count'].sum() * 100

fig, ax1 = plt.subplots()
ax1.bar(df['Category'], df['Count'], color='b', label='Frequency')
ax1.set_ylabel('Frequency', color='b')
ax1.set_xlabel('Category')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ax2.plot(df['Category'], df['Cumulative Percentage'], color='r', marker='o', linestyle='-', label='Cumulative %')
ax2.set_ylabel('Cumulative Percentage', color='r')
ax2.tick_params(axis='y', labelcolor='r')

plt.title('Pareto Chart')
plt.xticks(rotation=45)
plt.grid()
plt.savefig('pareto_chart.png', bbox_inches='tight')
