#! /usr/bin/python3

# packages needed: apt install  python3-urllib3  python3-bs4  python3-pil

# s.a. ~/Unterricht/LinuxLab-wlw/glal3_V4_station_list_from_www.listenlive.eu.py

import urllib.request
from bs4 import BeautifulSoup
import requests
from PIL import Image, ImageFont, ImageDraw
import os, time, re

URL = 'https://deepdreamgenerator.com/'   # trending
URL = 'https://deepdreamgenerator.com/latest'

RECYCLE_TIME = 10
TITLE_YPOS = 0.95
FONT_SIZE = 1/100   # of screen width
IMG_FILE = '/tmp/deepdream.jpg'
SCALING = 'scaled' # 'scaled' shows whole picture wheras 'zoom' fills screen with cropped picture

os.system(f'gsettings set org.gnome.desktop.background picture-options {SCALING}')
screen = re.findall(r' *(\d*)x(\d*)', os.popen("xrandr | grep '*'").read())[0]
screen_ratio = int(screen[0]) / int(screen[1])

conn = urllib.request.urlopen(URL)
html = conn.read()
soup = BeautifulSoup(html, "lxml")
scope = soup.find('div', attrs={'class':"feed light-gallery ddg-load-later"})
items = scope.find_all('div', attrs={'class':"content full-format"})

while True:
    images = []
    for item in items:
        img = item.find('img', attrs = {'data-sub-html':True})
        if img and img.has_attr('data-sub-html'):
            image = {}
            image['src'] = img['data-src']
            image['title'] = item.find('a', attrs={'class':"feed-dream-title"}).text.strip()
            image['autor'] = item.find('li', attrs={'class':"name"}).text.strip()
            images.append(image)

    for img in images:
        print(f"autor:'{img['autor']}'  title:'{img['title']}'  src:'{img['src']}'")

        img_data = requests.get(img['src']).content
        open(IMG_FILE, 'wb').write(img_data)

        # add image autor and title to image
        img_data = Image.open(IMG_FILE)
        xy = img_data.size
        y = xy[1]*TITLE_YPOS if (xy[0]/xy[1] > screen_ratio) or (SCALING=='scaled') else int(xy[1]/2 + xy[0]/2/screen_ratio*TITLE_YPOS)
        #print(xy, y)
        draw = ImageDraw.Draw(img_data)
        font = ImageFont.load_default().font_variant(size=xy[0]*FONT_SIZE)     #font = ImageFont.truetype("sans-serif.ttf", 16)
        draw.text((img_data.size[0]/2, y),f"{img['autor']} - {img['title']}",(255,255,255),font=font)
        img_data.save(IMG_FILE)

        os.system(f'gsettings set org.gnome.desktop.background picture-uri {IMG_FILE}')
        time.sleep(RECYCLE_TIME)

    time.sleep(RECYCLE_TIME)
