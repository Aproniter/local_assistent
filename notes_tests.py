import pytest
import os
from datetime import datetime
import random

from voice_buffer_parser import VoiceBufferParser
from note_creater import NoteCreater
from schemas import NoteBuffer
# from logger import logger as log
import commands
import db
import schemas


db.create_notes_table('test_db_path.db')
for i in os.listdir('test_notes'):
    os.remove(f'test_notes/{i}')


@pytest.fixture
def voice_buffer_parser():
    signal = 'note_creater'
    data = ['command 1', 'command 2', 'command 3']
    return VoiceBufferParser(signal, data, 'test_notes', 'test_db_path.db')

@pytest.fixture
def note_creater():
    data = ['command 1', 'command 2', 'command 3']
    buffer = NoteBuffer(header=None, all_data=data, tags=[])
    return NoteCreater(buffer, 'test_notes')


def test_notes_generator(note_creater):
    header = 'Test_Header'
    tags = ['tag1', 'tag2', 'tag3']

    note_body = note_creater._NoteCreater__notes_generator(header, tags)

    expected_body = '# TEST_HEADER\n\nCommand 1. Command 2. Command 3.\n\n[[tag1]] [[tag2]] [[tag3]]'
    assert note_body == expected_body

def test_note_creater(voice_buffer_parser):
    note_name = voice_buffer_parser.note_creater()
    
    note = db.get_note_by_final_text_or_header('test_db_path.db', note_name)
    assert note is not None
    assert os.path.exists(f'{voice_buffer_parser.notes_path}/{note_name}.md')
    
    with open(f'{voice_buffer_parser.notes_path}/{note_name}.md', 'r') as file:
        note_content = file.read()
        assert 'Command 1. Command 2. Command 3.\n\n' in note_content


def test_note_creater_with_header(voice_buffer_parser):
    header_phrase = commands.notes_header[random.randint(0,len(commands.notes_header) - 1)]
    voice_buffer_parser.data.extend([header_phrase, 'Test_Header'])
    voice_buffer_parser.note_creater()

    note = db.get_note_by_final_text_or_header('test_db_path.db', 'Test_Header')
    assert note is not None

    db_note = schemas.Note(*note[-1])
    assert db_note.file_name == 'Test_Header'

    assert os.path.exists(f'{voice_buffer_parser.notes_path}/Test_Header.md')

def test_note_creater_with_tags(voice_buffer_parser):
    header_phrase = commands.notes_header[random.randint(0,len(commands.notes_header) - 1)]
    note_name = 'Test_tags'
    voice_buffer_parser.data.extend([header_phrase, note_name])
    tags_phrase = commands.tags[random.randint(0,len(commands.tags) - 1)]
    tags = ['tag1', 'tag2', 'tag3']
    voice_buffer_parser.data.extend([tags_phrase, *tags])
    voice_buffer_parser.note_creater()
    
    with open(f'{voice_buffer_parser.notes_path}/{note_name}.md', 'r') as file:
        note_content = file.read()
        assert '[[tag1]] [[tag2]] [[tag3]]' in note_content

    for tag in tags:
        assert os.path.exists(f'{voice_buffer_parser.notes_path}/{tag}.md')
        with open(f'{voice_buffer_parser.notes_path}/{tag}.md', 'r') as file:
            note_content = file.read()
            assert f'[[{note_name}]]' in note_content

def test_create_linked_date_note(voice_buffer_parser):
    voice_buffer_parser.note_creater()
    current_date = datetime.now().strftime('%y-%m-%d')
    assert os.path.exists(f'{voice_buffer_parser.notes_path}/{current_date}.md')
