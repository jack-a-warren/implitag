from typing import List, Set
from lib.utils import get_db
import sqlite3


def get_item(item_id: int) -> sqlite3.Row:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT *
                FROM items
                WHERE item_id = ?
                """,
                (item_id,))
    item = cur.fetchone()
    conn.close()

    if item is None:
        raise ValueError(f"no item with id {item_id}")

    return item

def all_item_ids() -> Set[int]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT item_id
                FROM items
                """)
    items = cur.fetchall()
    conn.close()

    return set(item["item_id"] for item in items)

def all_listed_item_ids() -> Set[int]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT item_id
                FROM items
                WHERE unlisted = 0
                """)
    items = cur.fetchall()
    conn.close()

    return set(item["item_id"] for item in items)

# gets the names of an item's tags in alphabetical order
#
# item_id - the numeric id of the item
def get_item_tags(item_id: int) -> List[sqlite3.Row]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT tags.tag_id, tags.name
                FROM taggings
                INNER JOIN items USING (item_id)
                INNER JOIN tags USING (tag_id)
                WHERE items.item_id = ?
                ORDER BY tags.name
                """,
                (item_id,))
    tags = cur.fetchall()
    conn.close()

    return tags

# # determines whether item with a certain id has tag with a certain id
# def item_has_tag(item_id: int, tag_name: int) -> bool:
#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute("""
#                 SELECT 1
#                 FROM taggings
#                 JOIN tags USING (tag_id)
#                 WHERE 
#                     item_id = ?
#                     AND name = ?
#                 """,
#                 (item_id, tag_name))
#     conn.close()
#
#     return bool(cur.fetchone())
#
