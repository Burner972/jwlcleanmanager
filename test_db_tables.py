#!/usr/bin/env python3
"""
Simple test script to inspect SQLite database tables
"""

import sqlite3
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

# Configuration
TMP_PATH = mkdtemp(prefix='JWLManager_test_')
DB_NAME = 'userData.db'

def extract_jwlibrary(archive_path):
    """Extract .jwlibrary file to temp directory"""
    print(f"Extracting {archive_path}...")
    with ZipFile(archive_path, 'r') as zipped:
        zipped.extractall(TMP_PATH)
    print(f"Extracted to: {TMP_PATH}\n")

def list_all_tables():
    """List all tables in the database"""
    con = sqlite3.connect(f'{TMP_PATH}/{DB_NAME}')
    cursor = con.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("=" * 80)
    print("ALL AVAILABLE TABLES:")
    print("=" * 80)
    for i, table in enumerate(tables, 1):
        print(f"{i:2d}. {table}")
    
    print("\n" + "=" * 80)
    print("TABLES WITH 'DocumentId' COLUMN:")
    print("=" * 80)
    
    tables_with_docid = []
    for table in tables:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            if 'DocumentId' in columns:
                tables_with_docid.append(table)
                print(f"\n✓ {table}")
                print(f"  Columns: {', '.join(columns)}")
        except Exception as e:
            print(f"\n✗ Error checking {table}: {e}")
    
    if not tables_with_docid:
        print("⚠ No tables with 'DocumentId' column found!")
    
    # Check Location table specifically
    print("\n" + "=" * 80)
    print("LOCATION TABLE DETAILS:")
    print("=" * 80)
    
    try:
        cursor.execute("PRAGMA table_info(Location)")
        columns = cursor.fetchall()
        print("\nColumns in Location table:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check for DocumentId references
        cursor.execute("SELECT COUNT(*) FROM Location WHERE DocumentId IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"\nRows with non-NULL DocumentId: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    con.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_db_tables.py <path_to_archive.jwlibrary>")
        print("\nExample: python test_db_tables.py C:\\Users\\nardy\\Desktop\\myarchive.jwlibrary")
        sys.exit(1)
    
    archive_path = sys.argv[1]
    
    if not Path(archive_path).exists():
        print(f"Error: File '{archive_path}' not found!")
        sys.exit(1)
    
    try:
        extract_jwlibrary(archive_path)
        list_all_tables()
        print("\n" + "=" * 80)
        print("✓ Database inspection complete!")
        print("=" * 80)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
