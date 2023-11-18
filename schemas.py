from dataclasses import dataclass


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


@dataclass
class NoteBuffer:
    header: str | None
    all_data: list[str]
    tags: list[str] | None
    date: str | None # %Y-%m-%d
