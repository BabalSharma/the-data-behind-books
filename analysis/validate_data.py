import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "books.csv"

REQUIRED_COLUMNS = {
    "book_id", "authors", "title", "original_publication_year",
    "average_rating", "ratings_count",
    "ratings_1", "ratings_2", "ratings_3", "ratings_4", "ratings_5",
}


def main():
    if not DATA.exists():
        raise SystemExit(f"ERROR: Dataset not found: {DATA}")

    with DATA.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []
        rows = list(reader)

    errors = []
    warnings = []
    missing_columns = REQUIRED_COLUMNS - set(headers)

    print("DATA QUALITY REPORT")
    print("=" * 55)
    print(f"File: {DATA.relative_to(ROOT)}")
    print(f"Rows: {len(rows):,}")
    print(f"Columns: {len(headers)}")

    if missing_columns:
        errors.append(
            "Missing required columns: " + ", ".join(sorted(missing_columns))
        )
        print("\nRequired columns are missing; some checks cannot run.")
    elif not rows:
        errors.append("Dataset contains no data rows.")
    else:
        # Missing values in every column
        print("\n1. Missing values")
        for column in headers:
            count = sum(not (row.get(column) or "").strip() for row in rows)
            if count:
                print(f"  {column}: {count:,}")

        # Book ID uniqueness
        print("\n2. Book IDs")
        ids = [(row.get("book_id") or "").strip() for row in rows]
        blank_ids = sum(not value for value in ids)
        duplicates = sum(
            count > 1
            for count in Counter(value for value in ids if value).values()
        )
        print(f"  Blank IDs: {blank_ids:,}")
        print(f"  Duplicate ID values: {duplicates:,}")
        if blank_ids or duplicates:
            errors.append("Blank or duplicate book IDs found.")

        # Average rating range
        print("\n3. Average ratings")
        invalid_ratings = 0
        for row in rows:
            try:
                rating = float(row["average_rating"])
                if not 0 <= rating <= 5:
                    invalid_ratings += 1
            except (ValueError, TypeError):
                invalid_ratings += 1
        print(f"  Invalid or missing ratings: {invalid_ratings:,}")
        if invalid_ratings:
            errors.append(f"{invalid_ratings} invalid average ratings.")

        # Publication-year classification
        print("\n4. Publication years")
        blank_years = 0
        ref_errors = 0
        other_invalid = 0
        valid_years = []

        for row in rows:
            value = (row.get("original_publication_year") or "").strip()

            if not value:
                blank_years += 1
                continue

            if value.upper() == "#REF!":
                ref_errors += 1
                continue

            try:
                year = float(value)
                if year.is_integer() and 1 <= year <= 2026:
                    valid_years.append(int(year))
                else:
                    other_invalid += 1
            except ValueError:
                other_invalid += 1

        print(f"  Valid years: {len(valid_years):,}")
        print(f"  Blank years: {blank_years:,}")
        print(f"  #REF! spreadsheet errors: {ref_errors:,}")
        print(f"  Other invalid years: {other_invalid:,}")

        if valid_years:
            print(f"  Valid year range: {min(valid_years)}–{max(valid_years)}")

        if blank_years or ref_errors or other_invalid:
            warnings.append("Some publication years are missing or invalid.")

        # Count validity
        print("\n5. Count columns")
        count_columns = [
            "ratings_count", "ratings_1", "ratings_2",
            "ratings_3", "ratings_4", "ratings_5",
        ]
        invalid_counts = 0

        for column in count_columns:
            for row in rows:
                try:
                    if int(row[column]) < 0:
                        invalid_counts += 1
                except (ValueError, TypeError):
                    invalid_counts += 1

        print(f"  Invalid, missing, or negative count cells: {invalid_counts:,}")
        if invalid_counts:
            errors.append(f"{invalid_counts} invalid count cells.")

        # Repeated titles
        print("\n6. Repeated titles")
        titles = Counter(
            (row.get("title") or "").strip().casefold()
            for row in rows
            if (row.get("title") or "").strip()
        )
        repeated_titles = sum(count > 1 for count in titles.values())
        print(f"  Title values appearing multiple times: {repeated_titles:,}")
        print("  Repeated titles are not necessarily duplicate books.")

    print("\n" + "=" * 55)
    print(f"Errors: {len(errors)}")
    for message in errors:
        print(f"  ERROR: {message}")

    print(f"Warnings: {len(warnings)}")
    for message in warnings:
        print(f"  WARNING: {message}")

    if errors:
        raise SystemExit(1)

    print("\nValidation completed. Review warnings before analysis.")


if __name__ == "__main__":
    main()
