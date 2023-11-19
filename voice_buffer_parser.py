import os
import threading
from datetime import datetime

import commands
import config
import db
from note_creater import NoteCreater
from page_loader import PageLoader
from screen_parser import ScreenParser
from schemas import NoteBuffer
from logger import logger as log


class VoiceBufferParser:
    def __init__(self, signal, data, notes_path, db_path) -> None:
        self.notes_path = notes_path
        self.note_date = datetime.now().strftime('%y-%m-%d')
        self.db_path = db_path
        self.worker = self.__getattribute__(signal)
        self.data: list[str] = data
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()

    def save_internet_page(self):
        note_date = datetime.now().strftime('%y-%m-%d %H:%M:%S')
        links, corrected_links = ScreenParser().run()
        pages = PageLoader(links, corrected_links).run()
        tags = config.download_page_tags
        for page in pages:
            log.info(page.folder)
            all_data = [page.folder, commands.create_paragraph[0], *links, commands.create_paragraph[0], note_date]
            NoteCreater(NoteBuffer(page.name, all_data, tags), self.notes_path, True).run()
            self._edit_or_create_linked_note(note_date.split(' ')[0], page.name)
            self._edit_or_create_linked_note(config.download_page_tags[0], page.name)

    def note_creater(self) -> str:
        note_header = None
        tags = []
        tags_start = None
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
        tags.append(self.note_date)
        note_body, note_name = NoteCreater(NoteBuffer(note_header, self.data, tags), self.notes_path).run()
        for tag in tags:
            self._edit_or_create_linked_note(tag, note_name)
        db.save_voice_command_to_db(self.db_path, note_header, self.data, tags, self.note_date, note_body, note_name)
        return note_name
    
    def _edit_or_create_linked_note(self, main_note_header, note_name):
        if f'{main_note_header}.md' not in os.listdir(self.notes_path):
            NoteCreater(
                NoteBuffer(main_note_header, [], [note_name]),
                self.notes_path
            ).run()
        else:
            with open(f'{self.notes_path}/{main_note_header}.md', 'a') as dayli_file:
                dayli_file.write(f'\n\n[[{note_name}]]')


if __name__ == '__main__':
    v = VoiceBufferParser('save_internet_page', ['test'], config.notes_path, config.db_path)