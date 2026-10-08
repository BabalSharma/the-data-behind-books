import csv
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "books.csv"
CHARTS = ROOT / "charts"
CHARTS.mkdir(exist_ok=True)

rating_counts = []
average_ratings = []

with DATA.open(encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        try:
            count = int(row["ratings_count"])
            rating = float(row["average_rating"])
        except (ValueError, TypeError, KeyError):
            continue

        if count > 0 and 0 <= rating <= 5:
            rating_counts.append(count)
            average_ratings.append(rating)

plt.figure(figsize=(10, 6))
plt.scatter(rating_counts, average_ratings, alpha=0.35, s=18)
plt.xscale("log")
plt.xlabel("Number of ratings (log scale)")
plt.ylabel("Average book rating")
plt.title("Book Popularity vs Average Rating")
plt.ylim(0, 5)
plt.grid(True, alpha=0.25)
plt.tight_layout()

output = CHARTS / "rating_count_relationship.png"
plt.savefig(output, dpi=200)
plt.close()

print(f"Books plotted: {len(rating_counts):,}")
print(f"Chart saved to: {output.relative_to(ROOT)}")
