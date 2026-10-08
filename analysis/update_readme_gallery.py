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
    # Match the Google Sheet: rank by number of ratings, highest first.
    eligible.sort(
        key=lambda r: (
            -r["_count"],
            r["title"].casefold(),
        )
    )
    top = eligible[:10]
    lines = [
        START,
        "## Top 10 Most-Rated Books",
        "",
        "*Ranked by ratings count, matching the Google Sheet. Average ratings are displayed rounded to whole numbers.",
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
            f"| {row['_rating']:.0f} | {row['_count']:,} |"
        )
    lines.extend([
        "",
        "### Method",
        "",
        (
            "Calculated from `data/books.csv`. Books need at least 10,000 "
            "ratings to qualify. Books are ranked by ratings count, highest "
            "first, to match the supplied Google Sheet. Average ratings are "
            "rounded to whole numbers. Ratings reflect this dataset, not "
            "necessarily current Goodreads ratings."
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
    print("Ranking: ratings count, highest first.")
    print(f"Gallery entries: {len(top)}")
    print(f"Minimum ratings: {MIN_RATINGS:,}")
    print("Placeholder cover images excluded.")
if __name__ == "__main__":
    main()
