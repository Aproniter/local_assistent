import os
import subprocess
import requests

from schemas import PageToNote
# from logger import logger as log


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
        new_folder = f'{os.getenv("pages_folder")}/{title}'
        if title not in os.listdir(os.getenv("pages_folder")):
            os.mkdir(new_folder)
        command = f'wget -kpE -e robots=off {link}'
        subprocess.call(
            command,
            shell=True,
            cwd=new_folder,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        t = self.__get_obsidian_path(new_folder)
        return PageToNote(title, new_folder, t)

    def __get__list_links(self):
        return self.links if self.links == self.cor_links else [*self.links, *self.cor_links]
    
    def __get_obsidian_path(self, new_folder):
        for root, dirs, files in os.walk(new_folder):
            for file in files:
                if file == 'index.html':
                    tmp = os.path.join(root, file)
                    tmp = os.getenv('obsidian_prefix') + tmp[tmp.find(os.getenv('obsidian_prefix'))+len(os.getenv('obsidian_prefix')):]
                    return tmp


if __name__ == '__main__':
    p = PageLoader(['https://habr.com/ru/articles/589389/'],['https://habr.com/ru/articles/589389/'])
    # p = PageLoader(['https://stackoverflow.com/questions/12150612'],['https://stackoverflow.com/questions/12150612'])
    # p = PageLoader(['https://www.google.com/maps/@46.3611769,48.0292774,14z?entry=ttu'],['https://www.google.com/maps/@46.3611769,48.0292774,14z?entry=ttu'])
    p.run()
