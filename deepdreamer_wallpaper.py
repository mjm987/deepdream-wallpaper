#! /usr/bin/python3

# (c) 2025, Matthias Meier, licenced under Apache V2

# additional phyton packages needed: apt install  python3-urllib3  python3-bs4  python3-pil

# debugging dbus screensaver and presence state might be done by gdbus eg. by:
# gdbus introspect --session -r --dest org.gnome.ScreenSaver --object-path /org/gnome/ScreenSaver
# gdbus call --session --dest org.gnome.ScreenSaver --object-path /org/gnome/ScreenSaver --method org.gnome.ScreenSaver.GetActive
# gdbus call -e -d org.gnome.SessionManager -o /org/gnome/SessionManager/Presence -m org.freedesktop.DBus.Properties.Get org.gnome.SessionManager.Presence status

import urllib.request
from bs4 import BeautifulSoup
import requests
from PIL import Image, ImageFont, ImageDraw
import os, time, re, datetime, sys
import dbus

URL = 'https://deepdreamgenerator.com/'+(sys.argv[1] if len(sys.argv)>1 else '')  # default is 'trending' optional cmd argument 'latest', 'best/today', 'best/week', best/most-commented, ...

RECYCLE_TIME = 60
SCALING = 'scaled' # 'scaled' shows whole picture wheras 'zoom' fills screen with image cropped

TITLE_YPOS = 0.95
FONT_SIZE = 1/70   # of screen width
IMG_FN = '/tmp/deepdream'

os.system(f'gsettings set org.gnome.desktop.background picture-options {SCALING}')
screen = re.findall(r' *(\d*)x(\d*)', os.popen("xrandr | grep '*'").read())[0]
screen_ratio = int(screen[0]) / int(screen[1])


try:
    presence = dbus.SessionBus().get_object('org.gnome.SessionManager', '/org/gnome/SessionManager/Presence')
    screen_invisible = lambda : dbus.Interface(presence, dbus.PROPERTIES_IFACE).Get('org.gnome.SessionManager.Presence', 'status')!=0
    screen_invisible()
except:
    try:
        screensaver = dbus.SessionBus().get_object('org.gnome.ScreenSaver', '/org/gnome/ScreenSaver')
        screen_invisible = lambda : screensaver.GetActive(dbus_interface='org.gnome.ScreenSaver')!=0
        screen_invisible()
    except:
        print("Warning: no valid D-Bus object found neither for ScreenSaver nor SessionManager.Presence")
        screen_invisible = lambda : False

while True:
    try:
        conn = urllib.request.urlopen(URL)
        html = conn.read()
    except:
        print("Unable to download picture from {img['src']}. Try next in {RECYCLE_TIME}s")
        time.sleep(RECYCLE_TIME)
        continue
    soup = BeautifulSoup(html, 'lxml')
    scope = soup.find('div', attrs={'class':'feed light-gallery ddg-load-later'})
    items = scope.find_all('div', attrs={'class':'content full-format'})
    images = []
    for item in items:
        img = item.find('img', attrs = {'data-sub-html':True})
        if img and img.has_attr('data-sub-html'):
            image = {}
            image['src'] = img['data-src']
            image['title'] = item.find('a', attrs={'class':'popup-info', 'ddg-popup-title':True})
            image['title'] = image['title']['ddg-popup-title'].replace('Share ','')  if image['title'] else item.find('a', attrs={'class':'feed-dream-title'}).text.strip()
            #image['title'] = item.find('a', attrs={'class':'feed-dream-title'}).text.strip()
            image['autor'] = item.find('li', attrs={'class':'name'}).text.strip()
            images.append(image)

    if not images:
        print(f'Site {URL} not reachable or html structure changed!')
        time.sleep(RECYCLE_TIME)
        continue
    else:
        print(f'Picture list reloaded')

    for img in images:
        while screen_invisible():
            print("waiting...")
            time.sleep(RECYCLE_TIME)
        print(f"{datetime.datetime.now().time()}  {img['autor']} - {img['title']} - {img['src']}")
        try:
            im = requests.get(img['src']).content
        except:
            print("Unable to download picture from {img['src']}. Try next in {RECYCLE_TIME}s")
            time.sleep(RECYCLE_TIME)
            continue
        open(IMG_FN, 'wb').write(im)

        # add image autor and title to image and set background color in case picture has different aspect ration than screen
        im = Image.open(IMG_FN)
        xy = im.size
        col = (0,0,0)
        for i in range(xy[1]//3, xy[1]*2//3, xy[1]//30):
            col = map(sum, zip(col, im.getpixel((10, i)),im.getpixel((xy[0]-10, i))))
        col = [x//20 for x in col]
        os.system(f"gsettings set org.gnome.desktop.background primary-color '#{col[0]:02x}{col[1]:02x}{col[2]:02x}'")

        y = xy[1]*TITLE_YPOS if (xy[0]/xy[1] > screen_ratio) or (SCALING=='scaled') else int(xy[1]/2 + xy[0]/2/screen_ratio*TITLE_YPOS)
        draw = ImageDraw.Draw(im)
        try:
            font = ImageFont.truetype("FreeSans.ttf", xy[1]*FONT_SIZE)
        except:
            font = ImageFont.load_default().font_variant(size=xy[1]*FONT_SIZE)
        draw.text((im.size[0]/2, y), f"{img['autor']} - {img['title']}", (255,255,255), font=font)

        suffix = img['src'].split('?')[0][-4:]
        im.save(IMG_FN+suffix)
        os.system(f'gsettings set org.gnome.desktop.background picture-uri {IMG_FN+suffix}')
        time.sleep(RECYCLE_TIME)
