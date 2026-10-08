import csv
import html
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
CSV_FILE = ROOT / "data" / "books.csv"
README_FILE = ROOT / "README.md"
MIN_RATINGS = 10_000
START = "<!-- TOP_BOOKS_START -->"
END = "<!-- TOP_BOOKS_END -->"
def main():
    with CSV_FILE.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    eligible = []
    for row in rows:
        try:
            rating = float(row["average_rating"])
            count = int(row["ratings_count"])
        except (ValueError, TypeError, KeyError):
            continue
        if count < MIN_RATINGS or not row.get("title", "").strip():
            continue
        row["_rating"] = rating
        row["_count"] = count
        eligible.append(row)
    # Keep the highest-ranked eligible book for each author.
    eligible.sort(
        key=lambda r: (
            -r["_rating"],
            -r["_count"],
            r["title"].casefold(),
        )
    )
    top = []
    seen_authors = set()
    for row in eligible:
        authors = row.get("authors", "").strip()
        # Do not combine or split co-author names: treat the full author
        # field as one group to avoid making unsupported assumptions.
        names = [
            name.strip().casefold()
            for name in authors.split(",")
            if name.strip() and name.strip().casefold() != "anonymous"
        ]
        # Skip entries with anonymous authors or no identifiable author.
        if not names or "anonymous" in authors.casefold():
            continue
        # Skip a book if any named author has already appeared.
        if any(name in seen_authors for name in names):
            continue
        seen_authors.update(names)
        top.append(row)
        if len(top) == 10:
            break
    lines = [
        START,
        "## Top 10 Books by Average Rating",
        "",
        "*Eligibility: at least 10,000 ratings. No named author appears more than once; ranked by average rating, then rating count, then title.",
        "",
        "| Rank | Cover | Book | Author | Average rating | Ratings |",
        "|---:|---|---|---|---:|---:|",
    ]
    for rank, row in enumerate(top, start=1):
        title = row["title"].strip()
        author = row.get("authors", "").strip() or "Unknown"
        book_id = row.get("goodreads_book_id", "").strip()
        cover = (
            row.get("image_url", "").strip()
            or row.get("small_image_url", "").strip()
        )
        # Exclude the dataset's known Goodreads no-cover placeholder.
        if "nophoto" in cover.casefold():
            cover = ""
        safe_title = html.escape(title, quote=True)
        safe_author = html.escape(author, quote=True)
        safe_url = html.escape(cover, quote=True)
        cover_cell = (
            f'<img src="{safe_url}" alt="Cover of {safe_title}" width="65">'
            if cover.startswith(("https://", "http://"))
            else "Cover unavailable"
        )
        book_cell = (
            f"[{title.replace('[', '\\[').replace(']', '\\]')}]"
            f"(https://www.goodreads.com/book/show/{book_id})"
            if book_id.isdigit()
            else title
        )
        lines.append(
            f"| {rank} | {cover_cell} | {book_cell} | {safe_author} "
            f"| {row['_rating']:.2f}/5 | {row['_count']:,} |"
        )
    lines.extend([
        "",
        "### Method",
        "",
        (
            "Calculated from `data/books.csv`. Books need at least 10,000 "
            "ratings to qualify. The ranking uses average rating, then "
            "ratings count, then title. No named author appears more than once. "
            "Entries listing Anonymous are excluded. Ratings reflect this dataset, not necessarily current Goodreads ratings."
        ),
        "",
        "### Cover image credits",
        "",
        (
            "Cover links come from the dataset. Some covers may be unavailable. "
            "Images remain the property of their respective rights holders; "
            "reuse permissions may vary."
        ),
        "",
        "### Author portraits",
        "",
        (
            "Author portraits are not included until each image can be matched "
            "to a reliable source and appropriate attribution."
        ),
        "",
        END,
    ])
    generated = "\n".join(lines)
    readme = README_FILE.read_text(encoding="utf-8")
    if START in readme and END in readme:
        before, rest = readme.split(START, 1)
        _, after = rest.split(END, 1)
        updated = before.rstrip() + "\n\n" + generated + "\n" + after.lstrip()
    else:
        updated = readme.rstrip() + "\n\n" + generated + "\n"
    README_FILE.write_text(updated, encoding="utf-8")
    print(f"Updated: {README_FILE}")
    print(f"Eligible books: {len(eligible):,}")
    print(f"Unique named authors represented: {len(seen_authors):,}")
    print(f"Gallery entries: {len(top)}")
    print(f"Minimum ratings: {MIN_RATINGS:,}")
    print("Placeholder cover images excluded.")
if __name__ == "__main__":
    main()
