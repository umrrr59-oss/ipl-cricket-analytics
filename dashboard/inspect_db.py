
import sqlite3
from pathlib import Path

files = [
    Path("data/raw/ipl.db"),
    Path("notebooks/ipl.db"),
]

for db in files:
    print("\n" + "=" * 40)
    print("DATABASE:", db)
    print("Exists:", db.exists())

    if not db.exists():
        continue

    with sqlite3.connect(db) as conn:
        print("File size:", db.stat().st_size, "bytes")

        tables = conn.execute("""
            SELECT name, type
            FROM sqlite_master
            WHERE type IN ('table', 'view')
            ORDER BY name
        """).fetchall()

        if not tables:
            print("No tables or views found.")

        for name, kind in tables:
            print(f"\n{kind}: {name}")
            columns = conn.execute(
                f'PRAGMA table_info("{name}")'
            ).fetchall()
            print(", ".join(c[1] for c in columns))
