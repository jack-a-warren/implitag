import argparse
import sqlite3
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("media_dir", type=Path)
parser.add_argument("static_dir", type=Path)
parser.add_argument("db_file", type=Path)

def prepare(file: Path, static_dir: Path):
    url = file.resolve().relative_to(static_dir.resolve())
    return (str(url),)

args = parser.parse_args()
conn = sqlite3.connect(args.db_file)
files = args.media_dir.iterdir()
files = map(lambda f: prepare(f, args.static_dir), files)

conn.executemany("""
                 INSERT OR IGNORE INTO items (url)
                 VALUES (?)
                 """,
                 files)
conn.commit()
conn.close()
