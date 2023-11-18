import os
import threading
from datetime import datetime

import commands
import db
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
        note_body = self.__notes_generator(note_header, tags)
        noname_notes_count = len([i for i in os.listdir(self.notes_path) if 'new_note_' in i])
        if note_date is not None:
            note_name = note_date
        elif note_date is None and note_header is not None:
            note_name = note_header
        else:
            note_name = f'new_note_{noname_notes_count + 1}'
        with open(f'{self.notes_path}/{note_name}.md', 'w') as new_file:
            new_file.write(note_body)
        db.save_voice_command_to_db(self.db_path, note_header, self.data, tags, note_date, note_body, note_name)
        return note_name

    def __notes_generator(self, header, tags):
        for phrase in self.data:
            if phrase in commands.create_paragraph:
                self.data[self.data.index(phrase) - 1] += '\n\n'
                self.data.pop(self.data.index(phrase))
        body = '. '.join((phrase.capitalize() for phrase in self.data)).replace('\n\n. ', '\n\n') + '.'
        note_string = ''
        if header:
            note_string += f'# {header.upper()}\n\n'
        note_string += f'{body}\n\n'
        if tags:
            tags = ' '.join((f'[[{tag}]]' for tag in tags))
            note_string += tags
        return note_string
