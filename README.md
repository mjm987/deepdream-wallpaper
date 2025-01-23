# deepdream-wallpaper
Shows and recycles trending or latest Images from https://deepdreamgenerator.com as Gnome wallpaper.

Installation:
- Install python dependencies via: apt install  python3-urllib3  python3-bs4  python3-pil python3-requests
- Start deepdreamer-wallpaper.py automatically at log-in as decribed here:
    https://help.gnome.org/users/gnome-help/stable/shell-apps-auto-start.html.en
- By default 'trending' images are shown (As when opening https://deepdreamgenerator.com interactively). 
  Or other lists by an optional cmd line argument, eg:
   'latest', 'best/today', 'best/week', best/most-commented, ...
- Image recycle time, picture scaling ('zoom' instead of 'scaled') etc. could be changed by global variables at top of python script.
