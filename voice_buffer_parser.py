import threading
from datetime import datetime

import commands
import db
from note_creater import NoteCreater
from schemas import NoteBuffer
# from logger import logger as log


class VoiceBufferParser:
    def __init__(self, signal, data, notes_path, db_path) -> None:
        self.notes_path = notes_path
        self.db_path = db_path
        self.worker = self.__getattribute__(signal)
        self.data: list[str] = data
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()

    def save_internet_page(self):
        pass

    def note_creater(self) -> str:
        note_date = None
        note_header = None
        tags = []
        tags_start = None
        for phrase in self.data:
            if phrase in commands.daily_note:
                note_date = datetime.now().strftime('%y-%m-%d')
                self.data.pop(self.data.index(phrase))
                break
        for phrase in self.data:
            if phrase in commands.notes_header:
                note_header = self.data.pop(self.data.index(phrase) + 1)
                self.data.pop(self.data.index(phrase))
        for tag in commands.tags:
            if tag in self.data:
                tags_start = self.data.index(tag)
                tags = self.data[tags_start + 1:]
                self.data = self.data[:tags_start]
                break
        creater = NoteCreater(self.notes_path, NoteBuffer(note_header, self.data, tags, note_date))
        note_body, note_name = creater.run()
        
        db.save_voice_command_to_db(self.db_path, note_header, self.data, tags, note_date, note_body, note_name)
        return note_name
