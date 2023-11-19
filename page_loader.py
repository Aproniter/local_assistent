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
        title = r[r.find('<title>')+len('<title>'):r.find('</title>')].replace(' ', '_').replace('/','_')
        new_folder = f'{config.pages_folder}/{title}'
        if title not in os.listdir(config.pages_folder):
            os.mkdir(new_folder)
        command = f'wget -kpE -e robots=off {link}'
        subprocess.call(
            command,
            shell=True,
            cwd=new_folder,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return PageToNote(title, new_folder)

    def __get__list_links(self):
        return self.links if self.links == self.cor_links else [*self.links, *self.cor_links]


if __name__ == '__main__':
    p = PageLoader(['https://habr.com/ru/articles/589389/'],['https://habr.com/ru/articles/589389/'])
    # p = PageLoader(['https://stackoverflow.com/questions/12150612'],['https://stackoverflow.com/questions/12150612'])
    # p = PageLoader(['https://www.google.com/maps/@46.3611769,48.0292774,14z?entry=ttu'],['https://www.google.com/maps/@46.3611769,48.0292774,14z?entry=ttu'])
    p.run()
