import os
import subprocess
import requests

import config
from schemas import PageToNote

class PageLoader:
    def __init__(self, links, corrected_links) -> None:
        self.links = links
        self.cor_links = corrected_links

    def run(self):
        links = self.__get__list_links()
        return tuple(self._save_page(link) for link in links)

    def _parse_pages(self, pages):
        return {

        }

    def _save_page(self, link):
        r = requests.get(link).text
        title = r[r.find('<title>')+len('<title>'):r.find('</title>')]
        before_pages_list = set(os.listdir(config.pages_folder))
        command = f'wget -kpE -e robots=off {link}'
        subprocess.call(
            command,
            shell=True,
            cwd=config.pages_folder,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        new_folder = tuple(i for i in os.listdir(config.pages_folder) if i not in before_pages_list)
        page_folder = new_folder[0] if len(new_folder) > 0 else ''
        return PageToNote(title.replace(' ', '_').replace('/','_'), page_folder)

    def __get__list_links(self):
        return self.links if self.links == self.cor_links else [*self.links, *self.cor_links]


if __name__ == '__main__':
    p = PageLoader(['https://habr.com/ru/articles/589389/'],['https://habr.com/ru/articles/589389/'])
    # p = PageLoader(['https://stackoverflow.com/questions/12150612'],['https://stackoverflow.com/questions/12150612'])
    # p = PageLoader(['https://www.google.com/maps/@46.3611769,48.0292774,14z?entry=ttu'],['https://www.google.com/maps/@46.3611769,48.0292774,14z?entry=ttu'])
    p.run()
