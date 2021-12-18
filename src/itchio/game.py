import re
import requests
import json
import os

import itchio.utils

class Game:   
    def __init__(self, data):
        self.data = data["game"]
        self.name = self.data["title"]
        self.publisher = self.data["user"]["username"]
        self.link = self.data["url"]

        self.id = data["id"]
        self.game_id = data["game_id"]
        
        matches = re.match(r"https://(.+)\.itch\.io/(.+)", self.link)
        self.game_slug = matches.group(2)
        self.publisher_slug = matches.group(1)

        self.files = []

    def load_downloads(self, token):
        self.downloads = []
        r = requests.get(f"https://api.itch.io/games/{self.game_id}/uploads?download_key_id={self.id}", headers={"Authorization": token})
        j = r.json()
        for d in j["uploads"]:
            self.downloads.append(d)
    
    def download(self, token):
        self.load_downloads(token)

        if not os.path.exists(self.publisher_slug):
            os.mkdir(self.publisher_slug)

        if not os.path.exists(f"{self.publisher_slug}/{self.game_slug}"):
            os.mkdir(f"{self.publisher_slug}/{self.game_slug}")

        with open(f"{self.publisher_slug}/{self.game_slug}.json", "w") as f:
            json.dump({
                "name": self.name,
                "publisher": self.publisher,
                "link": self.link,
                "itch_id": self.id,
                "game_id": self.game_id,
                "itch_data": self.data,
            }, f)

        for d in self.downloads:
            # Get UUID
            r = requests.post(f"https://api.itch.io/games/{self.game_id}/download-sessions", headers={"Authorization": token})
            j = r.json()
            print(j)

            # Download
            file = d['filename'] or d['display_name'] or d['id']
            url = f"https://api.itch.io/uploads/{d['id']}/download?api_key={token}&download_key_id={self.id}&uuid={j['uuid']}"
            itchio.utils.download_url(url, f"{self.publisher_slug}/{self.game_slug}/{file}", self.name +" - "+file)
