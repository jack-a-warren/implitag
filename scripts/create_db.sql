CREATE TABLE IF NOT EXISTS "items" (
	"item_id"	INTEGER NOT NULL UNIQUE,
	"url" TEXT NOT NULL UNIQUE,
  "thumbnail_url" TEXT UNIQUE,
	"title"	TEXT DEFAULT NULL,
	"unlisted"	INTEGER NOT NULL DEFAULT FALSE,
	PRIMARY KEY("item_id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "tags" (
  "tag_id" INTEGER NOT NULL UNIQUE,
  "name" TEXT NOT NULL UNIQUE,
  "description" TEXT,
  "disabled" INTEGER NOT NULL DEFAULT FALSE,
  PRIMARY KEY("tag_id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "taggings" (
  "item_id" INTEGER NOT NULL,
  "tag_id" INTEGER NOT NULL,
  PRIMARY KEY("item_id", "tag_id"),
  FOREIGN KEY("item_id") 
  REFERENCES "items"
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY("tag_id") 
  REFERENCES "tags"
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "implications" (
  "tag_id" INTEGER NOT NULL,
  "implied_tag_id" INTEGER NOT NULL,
  PRIMARY KEY ("tag_id", "implied_tag_id"),
  FOREIGN KEY("tag_id") 
  REFERENCES "tags"
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY("implied_tag_id") 
  REFERENCES "tags"("tag_id")
    ON UPDATE CASCADE
    ON DELETE CASCADE
);
