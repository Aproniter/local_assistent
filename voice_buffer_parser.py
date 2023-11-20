import os
import threading
from datetime import datetime, timedelta
from playsound import playsound

import commands
import db
from note_creater import NoteCreater
from page_loader import PageLoader
from screen_parser import ScreenParser
from schemas import NoteBuffer
# from logger import logger as log


class VoiceBufferParser:
    def __init__(self, signal, data, notes_path, db_path) -> None:
        self.notes_path = notes_path
        self.note_date = datetime.now().strftime(os.getenv('date_format'))
        self.db_path = db_path
        self.worker = self.__getattribute__(signal)
        self.data: list[str] = data
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()

    def save_internet_page(self):
        note_date = datetime.now().strftime(os.getenv('datetime_format'))
        links, corrected_links = ScreenParser().run()
        pages = PageLoader(links, corrected_links).run()
        tags = os.getenv('download_page_tags')
        for page in pages:
            all_data = [page.folder, commands.create_paragraph[0], f'[[{page.link_to_obsidian}]]', commands.create_paragraph[0], *links, commands.create_paragraph[0], note_date]
            NoteCreater(NoteBuffer(page.name, all_data, tags), self.notes_path).run()
            self._edit_or_create_linked_note(note_date.split(' ')[0], page.name)
            self._edit_or_create_linked_note(os.getenv('download_page_tags')[0], page.name)
        playsound(f'{os.getenv("sounds_path")}/understand.mp3', False)

    def note_creater(self) -> str:
        note_header = None
        tags = []
        tags_start = None
        for phrase in self.data:
            if phrase in commands.notes_names:
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

    def adding_report(self):
        week_dates = self.__get_dates_of_current_week()
        note_name = f'{os.getenv("report_header")} с {week_dates[0]} по {week_dates[6]}'
        note_body = [f'- {i}\n' for i in self.data]
        if f'{note_name}.md' not in os.listdir(self.notes_path):
            note_body = [f'{commands.notes_headers[0]}', self.note_date, *note_body]
            NoteCreater(
                NoteBuffer(note_name, note_body, []),
                self.notes_path
            ).run()
        else:
            with open(f'{self.notes_path}/{note_name}.md', 'r+') as dayli_file:
                note_content = dayli_file.read()
                if (header :=  f'## {self.note_date}.\n\n') not in note_content:
                    dayli_file.seek(0,2)
                    dayli_file.write(header)
                dayli_file.seek(0,2)
                dayli_file.write(''.join(note_body))
        self._edit_or_create_linked_note(self.note_date, note_name)

    def _edit_or_create_linked_note(self, main_note_header, note_name):
        if f'{main_note_header}.md' not in os.listdir(self.notes_path):
            NoteCreater(
                NoteBuffer(main_note_header, [], [note_name]),
                self.notes_path
            ).run()
        else:
            with open(f'{self.notes_path}/{main_note_header}.md', 'r+') as dayli_file:
                note_content = dayli_file.read()
                if f'\n\n[[{note_name}]]' not in note_content:
                    dayli_file.seek(0,2)
                    dayli_file.write(f'\n\n[[{note_name}]]')

    def __get_dates_of_current_week(self):
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())
        return [(monday + timedelta(days=day)).strftime('%Y-%m-%d') for day in range(7)]


if __name__ == '__main__':
    v = VoiceBufferParser('save_internet_page', ['test'], os.getenv('notes_path'), os.getenv('db_path'))