import sqlite3
import lib.constants as constants
from flask import url_for
import json


def get_config():
    with open(constants.CONFIG_FILE_PATH) as f:
        config = json.load(f)

    return config

def get_db():
    config = get_config()
    conn = sqlite3.connect(config["current_db"])
    conn.row_factory = sqlite3.Row
    return conn

def make_media_dicts(items):
    return [
        {
            "url": url_for("static", 
                            filename=item["thumbnail_url"] 
                            if item["thumbnail_url"] 
                            else item["url"]
                           ), 
            "is_video": item["url"].split(".")[-1] in ["mp4", "webm"],
            "item_id": item["item_id"],
            "title": item["title"],
        } 
        for item in items
    ]
