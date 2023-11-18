import sqlite3
from dataclasses import dataclass

from logger import logger as log


@dataclass
class Note:
    id: int
    file_name: str
    note_header: str
    buffer_text: str
    tags: str
    date_on: str
    final_text: str
    tags_wrong: bool
    date_on_wrong: bool


def create_devices_table(path_to_db):
    try:
        sqlite_connection = sqlite3.connect(
            path_to_db
        )
        check_table = (
            'SELECT name FROM sqlite_master '
            'WHERE type="table" AND name="notes_buffer";'
        )
        create_table = (
            'CREATE TABLE notes_buffer ('
            'id INTEGER PRIMARY KEY, '
            'file_name TEXT, '
            'note_header TEXT, '
            'buffer_text TEXT, '
            'tags TEXT, '
            'date_on TEXT, '
            'final_text TEXT, '
            'tags_wrong BOOLEAN, '
            'date_on_wrong BOOLEAN);'
        )
        cursor = sqlite_connection.cursor()
        cursor.execute(check_table)
        if len(cursor.fetchall()) == 0:
            cursor.execute(create_table)
            sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as e:
        log.error(f'SQL ERROR: {e}')
    finally:
        if sqlite_connection:
            sqlite_connection.close()

def get_note_by_final_text_or_header(path_to_db, search_text):
    try:
        sqlite_connection = sqlite3.connect(path_to_db)
        select_query = (
            'SELECT * FROM notes_buffer '
            f'WHERE final_text = "{str(search_text)}" OR note_header = "{str(search_text)}" OR file_name = "{str(search_text)}";'
        )
        cursor = sqlite_connection.cursor()
        cursor.execute(select_query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except sqlite3.Error as e:
        log.error(f'SQL ERROR: {e}')
    finally:
        if sqlite_connection:
            sqlite_connection.close()

def save_voice_command_to_db(
        path_to_db, note_header, buffer_text,
        tags, date_on, final_text, file_name
    ):
    try:
        sqlite_connection = sqlite3.connect(
            path_to_db
        )
        insert_data = (
            'INSERT INTO notes_buffer '
            '(file_name, note_header, buffer_text, tags, date_on, final_text, tags_wrong, date_on_wrong) '
            f'VALUES  ("{str(file_name)}", "{str(note_header)}", "{str(buffer_text)}", "{str(tags)}", '
            f'"{str(date_on)}", "{str(final_text)}", {False}, {False});'
        )
        cursor = sqlite_connection.cursor()
        cursor.execute(insert_data)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as e:
        log.error(f'SQL ERROR: {e}')
    finally:
        if sqlite_connection:
            sqlite_connection.close()




def delete_device_data(path_to_db, buffer_text):
    try:
        sqlite_connection = sqlite3.connect(
            path_to_db
        )
        del_device = (
            'DELETE from voice_buffer '
            f'WHERE buffer_text = "{str(buffer_text)}"'
        )
        cursor = sqlite_connection.cursor()
        cursor.execute(del_device)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as e:
        log.error(f'SQL ERROR: {e}')
    finally:
        if sqlite_connection:
            sqlite_connection.close()