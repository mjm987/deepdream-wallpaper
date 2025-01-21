#! /usr/bin/python3

# (c) 2025, Matthias Meier, licenced under Apache V2

# packages needed: apt install  python3-urllib3  python3-bs4  python3-pil

import urllib.request
from bs4 import BeautifulSoup
import requests
from PIL import Image, ImageFont, ImageDraw
import os, time, re

URL = 'https://deepdreamgenerator.com/'   # trending
#URL = 'https://deepdreamgenerator.com/latest'
RECYCLE_TIME = 60
SCALING = 'scaled' # 'scaled' shows whole picture wheras 'zoom' fills screen with cropped picture

TITLE_YPOS = 0.95
FONT_SIZE = 1/100   # of screen width
IMG_FILE = '/tmp/deepdream.jpg'

os.system(f'gsettings set org.gnome.desktop.background picture-options {SCALING}')
screen = re.findall(r' *(\d*)x(\d*)', os.popen("xrandr | grep '*'").read())[0]
screen_ratio = int(screen[0]) / int(screen[1])


while True:
    try:
        conn = urllib.request.urlopen(URL)
        html = conn.read()
    except:
        print("Unable to download picture from {img['src']}. Try next in {RECYCLE_TIME}s")
        time.sleep(RECYCLE_TIME)
        continue
    soup = BeautifulSoup(html, "lxml")
    scope = soup.find('div', attrs={'class':"feed light-gallery ddg-load-later"})
    items = scope.find_all('div', attrs={'class':"content full-format"})
    images = []
    for item in items:
        img = item.find('img', attrs = {'data-sub-html':True})
        if img and img.has_attr('data-sub-html'):
            image = {}
            image['src'] = img['data-src']
            #image['title'] = item.find('a', attrs={'class':"feed-dream-title"}).text.strip()
            image['title'] = item.find('a', attrs={'class':"popup-info", 'ddg-popup-title':True})
            image['title'] = image['title']['ddg-popup-title'] if image['title'] else item.find('a', attrs={'class':"popup-info", 'ddg-popup-title':True})
            image['autor'] = item.find('li', attrs={'class':"name"}).text.strip()
            images.append(image)

    if not images:
        print(f'Site {URL} not reachable or html structure changed!')
        time.sleep(RECYCLE_TIME)
        continue

    for img in images:
        print(f"autor:'{img['autor']}'  title:'{img['title']}'  src:'{img['src']}'")
        try:
            img_data = requests.get(img['src']).content
        except:
            print("Unable to download picture from {img['src']}. Try next in {RECYCLE_TIME}s")
            time.sleep(RECYCLE_TIME)
            continue
        open(IMG_FILE, 'wb').write(img_data)

        # add image autor and title to image and set background color in case picture has different aspect ration than screen
        img_data = Image.open(IMG_FILE)
        xy = img_data.size
        col = (0,0,0)
        for i in range(10):
            col = map(sum, zip(col, img_data.getpixel((10, xy[1]/3+i*xy[1]/15)),img_data.getpixel((xy[0]-10, xy[1]/3+i*xy[1]/15))))
        col = [x//20 for x in col]
        os.system(f"gsettings set org.gnome.desktop.background primary-color '#{col[0]:02x}{col[1]:02x}{col[2]:02x}'")


        y = xy[1]*TITLE_YPOS if (xy[0]/xy[1] > screen_ratio) or (SCALING=='scaled') else int(xy[1]/2 + xy[0]/2/screen_ratio*TITLE_YPOS)
        #print(xy, y)
        draw = ImageDraw.Draw(img_data)
        font = ImageFont.load_default().font_variant(size=xy[0]*FONT_SIZE)     #font = ImageFont.truetype("sans-serif.ttf", 16)
        draw.text((img_data.size[0]/2, y),f"{img['autor']} - {img['title']}",(255,255,255),font=font)
        # error in img_data.save() in case format is not JPG but file extension of temp file is '.jpg'
        suffix = img['src'].split('?')[0][-4:]
        img_data.save(IMG_FILE+suffix)
        os.system(f'gsettings set org.gnome.desktop.background picture-uri {IMG_FILE+suffix}')
        time.sleep(RECYCLE_TIME)
