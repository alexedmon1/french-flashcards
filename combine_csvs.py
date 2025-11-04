#!/usr/bin/env python3
"""
Combine all vocabulary CSV files into one master file with category column.

This creates a master vocabulary file: master_vocabulary.csv
Format: french,english,category[,gender]

Usage:
    python combine_csvs.py
"""

import csv
from pathlib import Path

# Configuration
OUTPUT_FILE = Path("master_vocabulary.csv")
EXCLUDE_FILES = {"missed.csv", "master_vocabulary.csv"}  # Don't include auto-generated files

def get_category_name(filename: str) -> str:
    """Extract category name from filename (remove .csv extension)"""
    return filename.replace('.csv', '')

def has_gender_column(rows: list) -> bool:
    """Check if any row has a 3rd column (gender)"""
    return any(len(row) >= 3 and row[2].strip() for row in rows)

def combine_csv_files():
    """Combine all vocabulary CSV files into one master file"""
    # Find all CSV files in vocabulary folder
    vocab_dir = Path('vocabulary')
    if not vocab_dir.exists():
        print("❌ vocabulary/ folder not found")
        return

    csv_files = sorted(vocab_dir.glob('*.csv'))
    csv_files = [f for f in csv_files if f.name not in EXCLUDE_FILES]

    if not csv_files:
        print("❌ No CSV files found in vocabulary/ folder")
        return

    print(f"Found {len(csv_files)} vocabulary files to combine:")
    for f in csv_files:
        print(f"  - {f.name}")

    all_entries = []
    has_any_gender = False

    # Read all CSV files
    for csv_file in csv_files:
        category = get_category_name(csv_file.name)

        with csv_file.open(newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

            # Check if this file has gender column
            file_has_gender = has_gender_column(rows)
            if file_has_gender:
                has_any_gender = True

            for row in rows:
                if len(row) >= 2:
                    french = row[0].strip()
                    english = row[1].strip()
                    gender = row[2].strip() if len(row) >= 3 else ""

                    all_entries.append({
                        'french': french,
                        'english': english,
                        'category': category,
                        'gender': gender
                    })

    # Remove duplicates (same french/english pair)
    seen = set()
    unique_entries = []
    duplicates = 0

    for entry in all_entries:
        key = (entry['french'].lower(), entry['english'].lower())
        if key not in seen:
            seen.add(key)
            unique_entries.append(entry)
        else:
            duplicates += 1

    print(f"\n📊 Statistics:")
    print(f"  Total entries found: {len(all_entries)}")
    print(f"  Duplicates removed: {duplicates}")
    print(f"  Unique entries: {len(unique_entries)}")
    print(f"  Has gender info: {'Yes' if has_any_gender else 'No'}")

    # Write combined file
    with OUTPUT_FILE.open('w', newline='', encoding='utf-8') as f:
        if has_any_gender:
            # Include gender column
            writer = csv.writer(f)
            for entry in unique_entries:
                writer.writerow([
                    entry['french'],
                    entry['english'],
                    entry['category'],
                    entry['gender']
                ])
        else:
            # No gender column needed
            writer = csv.writer(f)
            for entry in unique_entries:
                writer.writerow([
                    entry['french'],
                    entry['english'],
                    entry['category']
                ])

    print(f"\n✅ Combined file created: {OUTPUT_FILE}")
    print(f"\nFormat: french,english,category" + (",gender" if has_any_gender else ""))

    # Show sample entries
    print(f"\n📝 Sample entries:")
    for entry in unique_entries[:5]:
        if entry['gender']:
            print(f"  {entry['french']},{entry['english']},{entry['category']},{entry['gender']}")
        else:
            print(f"  {entry['french']},{entry['english']},{entry['category']}")

    print(f"\n💡 Usage:")
    print(f"  python3 flashcards.py")
    print(f"  python3 flashcards.py --srs")

if __name__ == "__main__":
    try:
        combine_csv_files()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
