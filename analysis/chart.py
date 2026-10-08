import csv
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "books.csv"
OUTPUT = ROOT / "charts"
OUTPUT.mkdir(exist_ok=True)

with DATA.open(encoding="utf-8-sig", newline="") as file:
    books = list(csv.DictReader(file))

if not books:
    raise SystemExit("No book records found in data/books.csv")

# 1. Distribution of average book ratings
ratings = [
    float(book["average_rating"])
    for book in books
    if book.get("average_rating", "").strip()
]

plt.figure(figsize=(9, 5))
plt.hist(ratings, bins=20, edgecolor="black")
plt.title("Distribution of Average Book Ratings")
plt.xlabel("Average rating")
plt.ylabel("Number of books")
plt.tight_layout()
plt.savefig(OUTPUT / "rating_distribution.png", dpi=160)
plt.close()

# 2. Ten authors appearing most often in the dataset
authors = Counter()
for book in books:
    for author in book.get("authors", "").split(","):
        author = author.strip()
        if author:
            authors[author] += 1

top_authors = authors.most_common(10)
names = [item[0] for item in top_authors][::-1]
counts = [item[1] for item in top_authors][::-1]

plt.figure(figsize=(10, 6))
plt.barh(names, counts)
plt.title("Top 10 Authors by Book Records")
plt.xlabel("Number of book records")
plt.ylabel("Author")
plt.tight_layout()
plt.savefig(OUTPUT / "top_authors.png", dpi=160)
plt.close()

# 3. Books by publication decade
years = []
for book in books:
    value = book.get("original_publication_year", "").strip()
    try:
        year = int(float(value))
        if 0 < year <= 2026:
            years.append(year)
    except (ValueError, TypeError):
        continue

decades = Counter((year // 10) * 10 for year in years)
decade_labels = sorted(decades)

plt.figure(figsize=(11, 5))
plt.bar([str(decade) for decade in decade_labels],
        [decades[decade] for decade in decade_labels])
plt.title("Books by Publication Decade")
plt.xlabel("Decade starting year")
plt.ylabel("Number of books")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(OUTPUT / "publication_decades.png", dpi=160)
plt.close()

print(f"Loaded {len(books):,} book records.")
print(f"Saved charts to: {OUTPUT}")
for filename in (
    "rating_distribution.png",
    "top_authors.png",
    "publication_decades.png",
):
    print(f" - {filename}")
