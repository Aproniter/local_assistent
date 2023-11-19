import os

import commands
import config
from schemas import NoteBuffer


class NoteCreater:
    def __init__(self, data: NoteBuffer, notes_path = config.notes_path, page: bool = False) -> None:
        self.page = page
        self.notes_path = notes_path
        self.data = data
        self.noname_notes_count = len([i for i in os.listdir(self.notes_path) if 'new_note_' in i])
        self.note_name = self._get_note_name()
        self.note_body = self.__notes_generator(data.header, data.tags)

    def run(self) -> tuple:
        with open(f'{self.notes_path}/{self.note_name}.md', 'w') as new_file:
            new_file.write(self.note_body)
        return self.note_body, self.note_name

    def __notes_generator(self, header, tags):
        for phrase in self.data.all_data:
            if phrase in commands.create_paragraph:
                self.data.all_data[self.data.all_data.index(phrase) - 1] += '\n\n'
                self.data.all_data.pop(self.data.all_data.index(phrase))
        phrases = (phrase for phrase in self.data.all_data)
        if not self.page:
            phrases = tuple(map(str.capitalize, phrases))
        body = '. '.join(phrases).replace('\n\n. ', '\n\n')
        note_string = ''
        if header:
            note_string += f'# {header.upper()}\n\n'
        note_string += f'{body}.\n\n' if body else '\n'
        if tags:
            tags = ' '.join((f'[[{tag}]]' for tag in tags))
            note_string += tags
        return note_string

    def _get_note_name(self):
        if self.data.header is not None:
            return self.data.header 
        else:
            return f'new_note_{self.noname_notes_count + 1}'
    
    # def _add_daylistamp(self):
    #     self.data.tags.append(datetime.now().strftime(config.date_format))