from lib.utils import get_db
import lib.constants as constants
from math import ceil


def get_pages_index(page_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
                SELECT count(item_id)
                FROM items
                WHERE unlisted = 0
                """)
    item_count = cur.fetchone()["count(item_id)"]
    return get_pages(page_id, item_count)

def get_pages(page_id, item_count):
    page_count = ceil(item_count / constants.ITEM_LIMIT)
    last_page_id = page_count - 1

    previous_page_id = page_id - 1 if page_id > 0 else page_id
    next_page_id = page_id + 1 if page_id < last_page_id else page_id

    page_links = [
            {"pid": 0, "text": "<<", "current": False, "active": True},
            {"pid": previous_page_id, "text": "<", "current": False, "active": page_id > 0}]

    for offset in range(-4, 5):
        new_page_id = page_id + offset

        if new_page_id < 0 or new_page_id > last_page_id:
            continue

        page_links.append({"pid": new_page_id, "text": new_page_id + 1, "current": offset == 0, "active": True})

    page_links += [
            {"pid": next_page_id, "text": ">", "current": False, "active": page_id < last_page_id},
            {"pid": last_page_id, "text": ">>", "current": False, "active": True}
            ]

    return page_links

def page_slice(seq, page_id):
    count = len(seq)
    start_index = page_id * constants.ITEM_LIMIT

    if start_index >= len(seq):
        start_index = count

    end_index = start_index + constants.ITEM_LIMIT

    if end_index > len(seq):
        end_index = count

    return seq[start_index:end_index]
