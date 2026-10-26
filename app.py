from flask import Flask, flash, redirect, render_template, abort, url_for, request, session
import random
import sqlite3
import lib.tags as taglib
import lib.pages as pageslib
import lib.items as itemslib
import lib.constants as constants
import lib.search as searchlib
from lib.utils import get_db, make_media_dicts, get_config
from pathlib import Path


app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret-key-that-doesnt-really-matter-with-this"

@app.route("/")
@app.route("/items")
def index():
    try:
        page_id = request.args.get("pid", type=int)
    except ValueError:
        return redirect(url_for("index"))

    if page_id == 0:
        return redirect(url_for("index"))

    if page_id is None:
        page_id = 0

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT item_id, url, title, thumbnail_url, unlisted
                FROM items
                WHERE unlisted = 0
                ORDER BY item_id DESC
                LIMIT ?
                OFFSET ?
                """,
                (constants.ITEM_LIMIT, page_id * constants.ITEM_LIMIT))
    items = cur.fetchall()
    conn.close()
    medias = make_media_dicts(items)
    page_links = pageslib.get_pages_index(page_id)

    return render_template("index.html",
                           medias=medias,
                           page_links=page_links,
                           all_tags=taglib.all_names(),
                           app_config=get_config())

@app.route("/items/<int:item_id>")
def view_item(item_id):
    if request.args.get("q") == "":
        return redirect(url_for("view_item", item_id=item_id))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT item_id, url, title
                FROM items
                WHERE item_id = ?;
                """,
                (item_id,))
    item = cur.fetchone()

    # item doesn't exist
    if not item:
        return abort(404, f"No item with id {item_id}")

    tags = itemslib.get_item_tags(item_id)
    tag_ids = (tag["tag_id"] for tag in tags)
    full_tags = set()

    for tag_id in tag_ids:
        implied_tag_ids = taglib.get_full_implied_ids(tag_id)
        full_tags |= implied_tag_ids

    full_tags = sorted(map(taglib.get_tag, full_tags), key=lambda tag: tag["name"])

    is_video = Path(item["url"]).suffix in constants.VIDEO_EXTENSIONS

    search_query = request.args.get("q")

    return render_template("view.html", 
                           item=item,
                           tags=tags,
                           full_tags=full_tags,
                           is_video=is_video, 
                           search_query=search_query,
                           all_tags=taglib.all_names(),
                           app_config=get_config())


@app.route("/items/update/<int:item_id>", methods=["GET"])
def edit_item(item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT item_id, title, url
                FROM items
                WHERE item_id = ?
                """,
                (item_id,))
    item = cur.fetchone()

    if not item:
        return abort(404)

    is_video = item["url"].split(".")[-1] in constants.VIDEO_EXTENSIONS

    tags = itemslib.get_item_tags(item_id)
    tag_names = (tag["name"] for tag in tags)

    conn.close()

    return render_template("edit.html",
                           item=item,
                           tag_names=tag_names,
                           is_video=is_video,
                           all_tags=taglib.all_names(),
                           app_config=get_config())

@app.route("/items/update/<int:item_id>", methods=["POST"])
def update_item(item_id):
    title = request.form["title"]

    if title == "":
        title = None

    conn = get_db()

    tag_ids = taglib.process_tag_input(request.form["tags"])
    tag_ids = taglib.minimise_tag_set(tag_ids)

    conn.execute("""
                 UPDATE items
                 SET title = ?
                 WHERE item_id = ?
                 """,
                 (title, item_id))

    # clear current taggings
    conn.execute("""
                 DELETE FROM taggings
                 WHERE item_id = ?
                 """,
                 (item_id,))

    # add new taggings
    conn.executemany("""
                     INSERT INTO taggings (item_id, tag_id)
                     VALUES (?, ?)
                     """,
                     [(item_id, tag_id) for tag_id in tag_ids])
    conn.commit()
    conn.close()

    return redirect(url_for('view_item', item_id=item_id))

@app.route("/items/delist/<int:item_id>")
def delist_item(item_id):
    conn = get_db()
    conn.execute("""
                 UPDATE items
                 SET unlisted = 1
                 WHERE item_id = ?
                 """,
                 (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/items/relist/<int:item_id>")
def relist_item(item_id):
    try:
        page_id = request.args.get("pid", type=int)
    except ValueError:
        page_id = 0

    if page_id is None:
        page_id = 0

    conn = get_db()
    conn.execute("""
                 UPDATE items
                 SET unlisted = 0
                 WHERE item_id = ?
                 """,
                 (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_delisted', pid=page_id))

@app.route("/items/delisted")
def view_delisted():
    try:
        page_id = request.args.get("pid", type=int)
    except ValueError:
        return redirect(url_for("index"))

    if page_id == 0:
        return redirect(url_for("view_delisted"))

    if page_id is None:
        page_id = 0

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT count(item_id)
                FROM items
                WHERE unlisted = 1
                """)
    item_count = cur.fetchone()["count(item_id)"]

    cur.execute("""
                SELECT item_id, url, title, thumbnail_url, unlisted
                FROM items
                WHERE unlisted = 1
                ORDER BY item_id DESC
                LIMIT ?
                OFFSET ?
                """,
                (constants.ITEM_LIMIT, page_id * constants.ITEM_LIMIT))
    items = list(cur.fetchall())
    conn.close()

    medias = make_media_dicts(items)
    page_links = pageslib.get_pages(page_id, item_count)

    return render_template("delisted_index.html",
                           medias=medias,
                           page_links=page_links,
                           page_id=page_id,
                           all_tags=taglib.all_names(),
                           app_config=get_config())

@app.route("/tags")
def tag_index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                SELECT tag_id, name
                FROM tags
                ORDER BY name
                """)
    tags = cur.fetchall()
    conn.close()
    
    return render_template("tags.html",
                           tags=tags,
                           all_tags=taglib.all_names(),
                           app_config=get_config())

@app.route("/tags/<int:tag_id>")
def view_tag(tag_id):
    try:
        tag = taglib.get_tag(tag_id)
        implies = sorted(taglib.get_directly_implied(tag_id), 
                         key=lambda tag: tag["name"])
        implied_by = sorted(taglib.get_directly_implying(tag_id),
                            key=lambda tag: tag["name"])

        implies_full = sorted(taglib.get_full_implied(tag_id),
                              key=lambda tag: tag["name"])
        implied_by_full = sorted(taglib.get_full_implying(tag_id),
                                 key=lambda tag: tag["name"])

    except ValueError:
        return abort(404, f"no tag with id {tag_id}")

    return render_template("tag_view.html",
                           tag=tag,
                           implies=implies,
                           implied_by=implied_by,
                           implies_full=implies_full,
                           implied_by_full=implied_by_full,
                           all_tags=taglib.all_names(),
                           app_config=get_config())

@app.route("/tags/edit/<int:tag_id>", methods=["GET"])
def edit_tag(tag_id):
    try:
        tag = taglib.get_tag(tag_id)
        # implies_names = get_implied_tag_names(tag_id)
        implies_names = sorted(map(lambda tag: tag["name"], taglib.get_directly_implied(tag_id)))
        # implied_by_names = get_implying_tag_names(tag_id)
        implied_by_names = sorted(map(lambda tag: tag["name"], taglib.get_directly_implying(tag_id)))
    except ValueError:
        return abort(404, f"no tag with id {tag_id}")

    return render_template("tag_edit.html",
                           tag=tag,
                           implies_names=implies_names,
                           implied_by_names=implied_by_names,
                           all_tags=taglib.all_names(),
                           app_config=get_config())

@app.route("/tags/edit/<int:tag_id>", methods=["POST"])
def update_tag(tag_id):
    name = request.form["name"].strip()
    description = request.form["description"].strip()
    implied_by_ids = taglib.process_tag_input(request.form["implied_by"])
    implies_ids = taglib.process_tag_input(request.form["implies"])

    implied_by_ids = taglib.minimise_tag_set_reversed(implied_by_ids)
    implies_ids = taglib.minimise_tag_set(implies_ids)

    if name == "":
        return render_template("issue.html", msg="Tag name must not be empty", all_tags=taglib.all_names())

    if description == "":
        description = None

    conn = get_db()
    try:
        conn.execute("""
                    UPDATE tags
                    SET name = ?,
                        description = ?
                    WHERE tag_id = ?
                    """,
                    (name, description, tag_id))
        conn.execute("""
                     DELETE FROM implications
                     WHERE implied_tag_id = ?
                     """,
                     (tag_id,))
        conn.executemany("""
                         INSERT INTO implications
                         VALUES (?, ?)
                         """,
                         [(implied_by_id, tag_id) for implied_by_id in implied_by_ids])
        conn.execute("""
                     DELETE FROM implications
                     WHERE tag_id = ?
                     """,
                     (tag_id,))
        conn.executemany("""
                         INSERT INTO implications
                         VALUES (?, ?)
                         """,
                         [(tag_id, implies_id) for implies_id in implies_ids])
        conn.commit()
    except sqlite3.IntegrityError:
        return render_template("issue.html",
                               msg="Tag name already exists",
                               all_tags=taglib.all_names(),
                               app_config=get_config())
    finally:
        conn.close()

    return redirect(url_for("view_tag", tag_id=tag_id))

@app.route("/tags/new", methods=["GET"])
def new_tag():
    return render_template("tag_new.html",
                           all_tags=taglib.all_names(),
                           app_config=get_config())

@app.route("/tags/new", methods=["POST"])
def create_tag():
    name = request.form["name"].strip()
    description = request.form["description"].strip()
    implied_by_ids = taglib.process_tag_input(request.form["implied_by"])
    implies_ids = taglib.process_tag_input(request.form["implies"])

    implied_by_ids = taglib.minimise_tag_set_reversed(implied_by_ids)
    implies_ids = taglib.minimise_tag_set(implies_ids)

    if name == "":
        return render_template("issue.html",
                               msg="Tag name must not be empty",
                               all_tags=taglib.all_names(),
                               app_config=get_config())

    if description == "":
        description = None

    conn = get_db()
    try:
        conn.execute("""
                     INSERT INTO tags (name, description)
                     VALUES (?, ?)
                     """,
                     (name, description))
        cur = conn.cursor()
        cur.execute("""
                    SELECT tag_id
                    FROM tags
                    WHERE name = ?
                    """,
                    (name,))
        tag_id = cur.fetchone()["tag_id"]
        conn.executemany("""
                         INSERT INTO implications
                         VALUES (?, ?)
                         """,
                         [(implied_by_id, tag_id) for implied_by_id in implied_by_ids])
        conn.executemany("""
                         INSERT INTO implications
                         VALUES (?, ?)
                         """,
                         [(tag_id, implies_id) for implies_id in implies_ids])
        conn.commit()
    except sqlite3.IntegrityError:
        return render_template("issue.html",
                               msg="Tag already exists",
                               all_tags=taglib.all_names(),
                               app_config=get_config())
    finally:
        conn.close()

    return redirect(url_for("view_tag", tag_id=tag_id))

@app.route("/search")
def search():
    try:
        page_id = request.args.get("pid", type=int)
    except ValueError:
        flash("Invalid page id")
        return redirect(url_for("index"))

    if page_id is None:
        page_id = 0

    query = request.args.get("q")

    if query is None:
        return abort(400)

    segments = query.strip().split()

    if len(segments) == 0:
        return redirect(url_for("index"))

    try:
        result_ids = searchlib.run_query(segments)
    except searchlib.TooManyOperatorsError:
        flash(f"query error: too many operators")
        return redirect(url_for('index'))
    except ValueError:
        # used non-existent tag
        flash(f"query error: non-existent tag")
        return redirect(url_for('index'))

    result_ids = list(filter(lambda i: itemslib.get_item(i)["unlisted"] == 0, result_ids))

    item_count = len(result_ids)

    result_ids = sorted(list(result_ids), reverse=True)
    result_ids = pageslib.page_slice(result_ids, page_id)
    items = map(itemslib.get_item, result_ids)

    medias = make_media_dicts(items)
    page_links = pageslib.get_pages(page_id, item_count)

    return render_template("search_result.html",
                           medias=medias,
                           page_links=page_links,
                           result_count=item_count,
                           search_query=query,
                           all_tags=taglib.all_names(),
                           app_config=get_config())
                           
@app.route("/random")
def random_item():
    query = request.args.get("q")
    print(query)
    target_id = None

    if query is None:
        # pick random from all items
        target_id = random.choice(list(itemslib.all_item_ids()))
    else:
        segments = query.strip().split()

        if len(segments) == 0:
            target_id = random.choice(list(itemslib.all_item_ids()))
        else:
            try:
                print(f"running query for random with segments: {segments}")
                result_ids = searchlib.run_query(segments)
            except searchlib.TooManyOperatorsError:
                flash("random query error: too many operators")
                return redirect(url_for('index'))
            except ValueError:
                # used non-existent tag
                flash("random query error: non-existent tag")
                return redirect(url_for('index'))

            if len(result_ids) == 0:
                flash(f"random query error: no items found for query '{query}'")
                return redirect(url_for('index'))

            target_id = random.choice(list(result_ids))
    
    if target_id is None:
        flash("unknown error")
        return redirect(url_for("index"))

    return redirect(url_for("view_item", item_id=target_id, q=query))

if __name__ == "__main__":
    app.run(host="localhost", port=51069, debug=True)

