import pytesseract
import cv2
import numpy
from PIL import ImageGrab

import config


class ScreenParser:
    def __init__(self) -> None:
        self.screens = []
        self.links = []
        self.corrected_links = []

    def run(self):
        self.__get_screenshots()
        self.__find_links()
        self.__get_corrected_links()
        return self.links, self.corrected_links

    def __find_links(self):
        for img in self.screens:
            string = pytesseract.image_to_string(img)
            http_start = string.find('http')
            if http_start != -1:
                n = string.find('\n')
                string = string[http_start:] if n == -1 else string[http_start:n]
                string = string.replace('htm!', 'html').replace(' ', '_')
                self.links.append(string)
                self.__save_to_dataset(img, string)
            else:
                self.__save_to_dataset(img, string)

    def __get_screenshots(self):
        for key, screen_number in enumerate(config.my_brauser_link_regions):
            screenshot = ImageGrab.grab(bbox=screen_number)
            image = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            width = int(gray.shape[1] * config.scale_percent / 100)
            height = int(gray.shape[0] * config.scale_percent / 100)
            dim = (width, height)
            resize = cv2.resize(gray, dim, interpolation= cv2.INTER_LINEAR)
            self.screens.append(resize)

    def __get_corrected_links(self):
        for link in self.links:
            self.corrected_links.append(
                link.replace('O','0')
            )

    def __save_to_dataset(self, img, name):
        name = name.replace(':',f'%{hex(ord(":"))}').replace('/',f'%{hex(ord("/"))}').replace('\n','')
        cv2.imwrite(f'{config.screens_dataset_path}/{name}.jpg', img)



if __name__ == '__main__':
    s = ScreenParser()
    links = s.run()
 