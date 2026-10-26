import sqlite3
from lib.utils import get_db
from typing import List, Set
import lib.items as itemlib


def get_tag(tag_id: int) -> sqlite3.Row:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT tag_id, name, description
                FROM tags
                WHERE tag_id = ?
                """,
                (tag_id,))
    tag = cur.fetchone()
    conn.close()

    if tag is None:
        raise ValueError(f"no tag with id: {tag_id}")

    return tag

# get id of tag with name = tag_name
def get_tag_by_name(tag_name: str) -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT tag_id
                FROM tags
                WHERE name = ?
                """,
                (tag_name,))

    tag = cur.fetchone()
    conn.close()

    if tag is None:
        raise ValueError(f"no such tag: '{tag_name}'")

    return tag["tag_id"]

def get_directly_implying(tag_id: int, cur: sqlite3.Cursor | None = None):
    create_cursor = cur is None

    if create_cursor:
        conn = get_db()
        cur = conn.cursor()

    cur.execute("""
                SELECT t.tag_id, t.name
                FROM implications
                JOIN tags t USING (tag_id)
                WHERE implied_tag_id = ?
                """,
                (tag_id,))

    tags = cur.fetchall()

    if create_cursor:
        conn.close()

    return tags

def get_directly_implied(tag_id: int, cur: sqlite3.Cursor | None = None):
    create_cursor = cur is None

    if create_cursor:
        conn = get_db()
        cur = conn.cursor()

    cur.execute("""
                SELECT implied_tag_id tag_id, t.name
                FROM implications i
                JOIN tags t ON implied_tag_id = t.tag_id
                WHERE i.tag_id = ?
                """,
                (tag_id,))

    tags = cur.fetchall()

    if create_cursor:
        conn.close()

    return tags

def _get_direct_implying_tag_ids(tag_id: int, cur: sqlite3.Cursor) -> Set[int]:
    cur.execute("""
                SELECT tag_id
                FROM implications
                WHERE implied_tag_id = ?
                """,
                (tag_id,))

    return set([tag["tag_id"] for tag in cur.fetchall()])

def _get_direct_implied_tag_ids(tag_id: int, cur: sqlite3.Cursor) -> Set[int]:
    cur.execute("""
                SELECT implied_tag_id
                FROM implications
                WHERE tag_id = ?
                """,
                (tag_id,))

    return set([tag["implied_tag_id"] for tag in cur.fetchall()])

def get_full_implying_ids(tag_id: int) -> Set[int]:
    conn = get_db()
    cur = conn.cursor()

    search_stack = [tag_id]
    implying_tags = {tag_id}

    while len(search_stack) > 0:
        next_tag = search_stack.pop()
        children = _get_direct_implying_tag_ids(next_tag, cur)
        
        for child in children:
            if child not in implying_tags:
                search_stack.append(child)

        implying_tags |= children

    return implying_tags

def get_full_implied_ids(tag_id: int) -> Set[int]:
    conn = get_db()
    cur = conn.cursor()

    search_stack = [tag_id]
    implied_tags = {tag_id}

    while len(search_stack) > 0:
        next_tag = search_stack.pop()
        children = _get_direct_implied_tag_ids(next_tag, cur)
        
        for child in children:
            if child not in implied_tags:
                search_stack.append(child)

        implied_tags |= children

    return implied_tags

def get_full_implying(tag_id: int):
    tag_ids = get_full_implying_ids(tag_id) - {tag_id}
    return map(lambda tag_id: get_tag(tag_id), tag_ids)

def get_full_implied(tag_id: int):
    tag_ids = get_full_implied_ids(tag_id) - {tag_id}
    return map(lambda tag_id: get_tag(tag_id), tag_ids)

# remove any superfluous (ie, implied by some other tag in the set) tags
# from the set of ids
def minimise_tag_set(tag_ids: Set[int]) -> Set[int]:
    superfluous_tags = set()
    
    for tag_id in tag_ids:
        if len(tag_ids & (get_full_implying_ids(tag_id) - {tag_id})) > 0:
            superfluous_tags.add(tag_id)

    return tag_ids - superfluous_tags

def minimise_tag_set_reversed(tag_ids: Set[int]) -> Set[int]:
    superfluous_tags = set()
    
    for tag_id in tag_ids:
        if len(tag_ids & (get_full_implied_ids(tag_id) - {tag_id})) > 0:
            superfluous_tags.add(tag_id)

    return tag_ids - superfluous_tags

def all_names() -> List[str]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT name
                FROM tags
                ORDER BY name
                """)
    tags = cur.fetchall()
    conn.close()

    return [tag["name"] for tag in tags]

# convert list of tag names to ids, EXCLUDING NON-EXISTENT TAGS
# used when tags have been entered by user only
def process_tag_input(tag_input: str) -> Set[int]:
    names = tag_input.lower().strip().split()
    tag_ids = set()

    for name in names:
        try:
            tag = get_tag_by_name(name)
        except ValueError:
            # no tag with name `name`
            continue

        tag_ids.add(tag)

    return tag_ids

# gets the set of item ids that have tag with tag_id
def get_tag_item_ids(tag_id: int, exclude_unlisted=False) -> Set[int]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"""
                SELECT item_id
                FROM taggings
                JOIN items USING (item_id)
                WHERE tag_id = ?
                {'AND unlisted = 0' if exclude_unlisted else ''}
                """,
                (tag_id,))
    items = cur.fetchall()
    conn.close()

    return set(item["item_id"] for item in items)

def get_tag_items(tag_id: int):
    item_ids = get_tag_item_ids(tag_id)
    return map(itemlib.get_item, item_ids)

