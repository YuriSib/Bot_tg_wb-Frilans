create_users_table = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_user_id INTEGER,
  from_user_username TEXT,
  from_user_firstname TEXT,
  regtime INTEGER
);
"""

create_photo_table = """
CREATE TABLE IF NOT EXISTS user_photo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_user_id INTEGER,
  foto BLOB,
  msg_id INTEGER

);
"""
create_video_table = """
CREATE TABLE IF NOT EXISTS user_video (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_user_id INTEGER,
  video BLOB,
  msg_id INTEGER
);
"""
create_document_table = """
CREATE TABLE IF NOT EXISTS user_document (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_user_id INTEGER,
  document BLOB,
  msg_id INTEGER
);
"""

up_foto = """
INSERT INTO user_photo (
  from_user_id, 
  foto,
  msg_id
  )
VALUES (?,?,?)
"""

up_video = """
INSERT INTO user_video (
  from_user_id, 
  video,
  msg_id
  )
VALUES (?,?,?)
"""
up_document = """
INSERT INTO user_document (
  from_user_id, 
  document,
  msg_id
  )
VALUES (?,?,?)
"""
get_foto = """
SELECT msg_id, foto FROM user_photo WHERE from_user_id = ?
"""
get_video = """
SELECT msg_id, video FROM user_video WHERE from_user_id = ?
"""
get_document = """
SELECT msg_id, document FROM user_document WHERE from_user_id = ?
"""
save_user = """
INSERT INTO users (
  from_user_id,
  from_user_username,
  from_user_firstname,
  regtime
  )
VALUES (?,?,?,?)
"""

find_user = """
SELECT from_user_id FROM users WHERE from_user_id = ?
"""