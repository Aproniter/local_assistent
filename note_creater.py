import os

import commands
from schemas import NoteBuffer


class NoteCreater:
    def __init__(self, notes_path, data: NoteBuffer, page: bool = False) -> None:
        self.page = page
        self.notes_path = notes_path
        self.data = data
        self.note_body = self.__notes_generator(data.header, data.tags)
        self.noname_notes_count = len([i for i in os.listdir(self.notes_path) if 'new_note_' in i])

    def run(self) -> tuple:
        if self.data.date is not None:
            note_name = self.data.date
        elif self.data.date is None and self.data.header is not None:
            note_name = self.data.header 
        else:
            note_name = f'new_note_{self.noname_notes_count + 1}'
        with open(f'{self.notes_path}/{note_name}.md', 'w') as new_file:
            new_file.write(self.note_body)
        return self.note_body, note_name

    def __notes_generator(self, header, tags):
        for phrase in self.data.all_data:
            if phrase in commands.create_paragraph:
                self.data.all_data[self.data.all_data.index(phrase) - 1] += '\n\n'
                self.data.all_data.pop(self.data.all_data.index(phrase))
        phrases = (phrase for phrase in self.data.all_data)
        if not self.page:
            phrases = tuple(map(str.capitalize, phrases))
        body = '. '.join(phrases).replace('\n\n. ', '\n\n') + '.'
        note_string = ''
        if header:
            note_string += f'# {header.upper()}\n\n'
        note_string += f'{body}\n\n'
        if tags:
            tags = ' '.join((f'[[{tag}]]' for tag in tags))
            note_string += tags
        return note_string