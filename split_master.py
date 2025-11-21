#!/usr/bin/env python3
"""
Split master_vocabulary.csv back into individual category files.

This is useful when you've been editing master_vocabulary.csv directly
and want to sync those changes back to the individual vocabulary files.

The script:
- Reads master_vocabulary.csv
- Groups entries by category
- Writes each category to vocabulary/<category>.csv
- Optionally converts pipe delimiters back to comma format

Usage:
    python split_master.py [options]

Options:
    --keep-pipes    Keep pipe delimiters (|) instead of converting to commas
                    Default: converts "as|like" to "as, like"
    --backup        Backup existing vocabulary folder before splitting
    --clean         Remove all existing CSV files before writing new ones
    --help, -h      Show this help message
"""

import csv
import sys
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
MASTER_FILE = Path("master_vocabulary.csv")
OUTPUT_DIR = Path("vocabulary")
KEEP_PIPES = "--keep-pipes" in sys.argv
DO_BACKUP = "--backup" in sys.argv
DO_CLEAN = "--clean" in sys.argv

def split_master_file():
    """Split master vocabulary file by category"""
    if not MASTER_FILE.exists():
        print(f"❌ Master file not found: {MASTER_FILE}")
        return

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Backup existing vocabulary folder if requested
    if DO_BACKUP and OUTPUT_DIR.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"vocabulary_backup_{timestamp}")
        print(f"📦 Creating backup: {backup_dir}/")
        shutil.copytree(OUTPUT_DIR, backup_dir)
        print(f"   ✓ Backup complete\n")

    # Clean existing CSV files if requested
    if DO_CLEAN and OUTPUT_DIR.exists():
        csv_files = list(OUTPUT_DIR.glob("*.csv"))
        if csv_files:
            print(f"🧹 Cleaning {len(csv_files)} existing CSV files...")
            for csv_file in csv_files:
                csv_file.unlink()
            print(f"   ✓ Cleanup complete\n")

    # Group entries by category
    categories = defaultdict(list)

    print(f"📖 Reading {MASTER_FILE}...")

    with MASTER_FILE.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                french = row[0].strip()
                english = row[1].strip()
                category = row[2].strip()
                gender = row[3].strip() if len(row) >= 4 else ""

                # Convert pipe delimiters back to comma-space (unless --keep-pipes)
                if not KEEP_PIPES:
                    french = french.replace('|', ', ')
                    english = english.replace('|', ', ')

                # Store entry with category
                entry = {
                    'french': french,
                    'english': english,
                    'gender': gender
                }
                categories[category].append(entry)

    if not categories:
        print("⚠️  No entries found in master file")
        return

    print(f"\n📊 Found {len(categories)} categories:")
    for category, entries in sorted(categories.items()):
        print(f"  • {category:<30} {len(entries):>4} entries")

    # Write each category to its own file
    print(f"\n✍️  Writing category files to {OUTPUT_DIR}/...")

    files_written = 0
    total_entries = 0

    for category, entries in sorted(categories.items()):
        # Create filename from category
        filename = f"{category}.csv"
        output_path = OUTPUT_DIR / filename

        # Write entries
        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            for entry in entries:
                # Check if any entry has gender info
                if entry['gender']:
                    # Write 3-column format: french,english,gender
                    writer.writerow([entry['french'], entry['english'], entry['gender']])
                else:
                    # Write 2-column format: french,english
                    writer.writerow([entry['french'], entry['english']])

        files_written += 1
        total_entries += len(entries)
        print(f"  ✓ {filename:<30} ({len(entries)} entries)")

    print(f"\n✅ Successfully split master file:")
    print(f"   Files written: {files_written}")
    print(f"   Total entries: {total_entries}")

    if not KEEP_PIPES:
        print(f"\n💡 Pipe delimiters (|) converted to comma-space (, )")
        print(f"   To keep pipes, use: python split_master.py --keep-pipes")
    else:
        print(f"\n💡 Pipe delimiters (|) preserved in output files")

    print(f"\n📝 Next steps:")
    print(f"   • Review the files in {OUTPUT_DIR}/")
    print(f"   • Run 'python combine_csvs.py' to regenerate master file")
    print(f"     (this converts commas back to pipes)")

def show_help():
    """Display help information"""
    print(__doc__)

if __name__ == "__main__":
    try:
        if "--help" in sys.argv or "-h" in sys.argv:
            show_help()
        else:
            split_master_file()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
