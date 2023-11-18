import pytest
from screen_parser import ScreenParser


@pytest.fixture
def mock_image_to_string(mocker):
    mock_image_to_string = mocker.patch('pytesseract.image_to_string')
    return mock_image_to_string

def test_find_links_without_http(mock_image_to_string):
    mock_image_to_string.return_value = 'Some text without links'
    parser = ScreenParser()
    parser._get_screenshots()
    parser._find_links()
    assert parser.links == []

def test_get_screenshots():
    parser = ScreenParser()
    parser._get_screenshots()
    assert len(parser.screens) == 2

def test_get_corrected_links():
    parser = ScreenParser()
    parser.links = ['http://example0.com', 'http://exampleO.org']
    parser._get_corrected_links()
    assert parser.corrected_links == ['http://example0.com', 'http://example0.org']
