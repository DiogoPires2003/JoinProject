import os
import requests
import matplotlib.pyplot as plt
from collections import Counter

# GitHub API setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}  # Update token type to Bearer

# Fetch issues
def fetch_issues():
    url = f"https://api.github.com/repos/{REPO}/issues"
    params = {"state": "all", "per_page": 100}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

# Process labels
issues = fetch_issues()
label_counts = Counter(label["name"] for issue in issues for label in issue.get("labels", []))

# Sort by frequency (Pareto principle)
sorted_labels = label_counts.most_common()
labels, counts = zip(*sorted_labels) if sorted_labels else ([], [])

# Cumulative percentage
cumulative = [sum(counts[:i+1]) / sum(counts) * 100 for i in range(len(counts))]

# Plot Pareto Chart
fig, ax1 = plt.subplots()

ax1.bar(labels, counts, color="royalblue", label="Issue Count")
ax1.set_ylabel("Issue Count", color="royalblue")
ax1.tick_params(axis="y", labelcolor="royalblue")

ax2 = ax1.twinx()
ax2.plot(labels, cumulative, color="crimson", marker="o", linestyle="-", label="Cumulative %")
ax2.set_ylabel("Cumulative Percentage", color="crimson")
ax2.tick_params(axis="y", labelcolor="crimson")

plt.title("Pareto Chart of GitHub Issues")
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig("pareto_chart.png", dpi=300)
