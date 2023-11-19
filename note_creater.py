import os

import commands
import config
from schemas import NoteBuffer
# from logger import logger as log


class NoteCreater:
    def __init__(self, data: NoteBuffer, notes_path = config.notes_path) -> None:
        self.notes_path = notes_path
        self.data = data
        self.noname_notes_count = len([i for i in os.listdir(self.notes_path) if 'new_note_' in i])
        self.note_name = self._get_note_name()
        self.note_body = self.__notes_generator(data.tags)

    def run(self) -> tuple:
        with open(f'{self.notes_path}/{self.note_name}.md', 'w') as new_file:
            new_file.write(self.note_body)
        return self.note_body, self.note_name

    def __notes_generator(self, tags):
        for phrase in self.data.all_data:
            if phrase in commands.create_paragraph:
                self.data.all_data[self.data.all_data.index(phrase) - 1] += '\n\n'
                self.data.all_data.pop(self.data.all_data.index(phrase))
            if phrase in commands.notes_headers:
                text_header = self.data.all_data[self.data.all_data.index(phrase) + 1]
                self.data.all_data[self.data.all_data.index(phrase) + 1] = f'\n\n## {text_header.capitalize()}.\n\n'
                self.data.all_data.pop(self.data.all_data.index(phrase))
        phrases = []
        for phrase in self.data.all_data:
            if '##' in phrase:
                phrases.append(phrase)
            else:
                phrases.append(phrase.capitalize())
        body = '. '.join(phrases).replace('\n\n. ', '\n\n')
        note_string = ''
        note_string += f'{body}.\n\n' if body else '\n'
        if tags:
            tags = ' '.join((f'[[{tag}]]' for tag in tags))
            note_string += tags
        return note_string

    def _get_note_name(self):
        if self.data.name is not None:
            return self.data.name .capitalize()
        else:
            return f'new_note_{self.noname_notes_count + 1}'
    
    # def _add_daylistamp(self):
    #     self.data.tags.append(datetime.now().strftime(config.date_format))