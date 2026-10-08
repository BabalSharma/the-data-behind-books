import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "books.csv"

checked = 0
mismatches = 0
invalid_rows = 0
examples = []

with DATA.open(encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        try:
            star_counts = [
                int(row[f"ratings_{stars}"])
                for stars in range(1, 6)
            ]
            reported_total = int(row["work_ratings_count"])
        except (ValueError, TypeError, KeyError):
            invalid_rows += 1
            continue

        if any(count < 0 for count in star_counts):
            invalid_rows += 1
            continue

        checked += 1
        calculated_total = sum(star_counts)

        if calculated_total != reported_total:
            mismatches += 1

            if len(examples) < 5:
                examples.append({
                    "book_id": row.get("book_id", ""),
                    "calculated": calculated_total,
                    "reported": reported_total,
                    "difference": reported_total - calculated_total,
                })

print("=" * 52)
print("RATING TOTAL CONSISTENCY AUDIT")
print("=" * 52)
print(f"Valid records checked: {checked:,}")
print(f"Invalid records skipped: {invalid_rows:,}")
print(f"Rating-total mismatches: {mismatches:,}")

if examples:
    print("\nFirst mismatches:")
    for item in examples:
        print(
            f"Book ID {item['book_id']}: "
            f"calculated={item['calculated']:,}, "
            f"reported={item['reported']:,}, "
            f"difference={item['difference']:,}"
        )

if checked == 0:
    print("\nERROR: No valid records could be checked.")
elif mismatches == 0:
    print("\nPASS: All checked rating totals match.")
else:
    print("\nREVIEW: Investigate mismatches before drawing conclusions.")
