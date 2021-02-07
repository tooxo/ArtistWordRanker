from collections import OrderedDict

import requests
from urllib.parse import quote
import json


class AlbumArt:
    def __init__(self, database):
        self.base_url = (
            "https://itunes.apple.com/search?media=music&limit=50&term="
        )
        self.database = database

    def get_artist(self, artist_name):
        temp = self.database.get_album_art(artist_name)
        if temp:
            return temp
        with requests.get(
            self.base_url + quote(artist_name), verify=False
        ) as g:
            json_response = g.json()["results"]
            urls = list(
                OrderedDict.fromkeys(
                    map(
                        lambda x: (x["collectionName"], x["artworkUrl100"]),
                        filter(lambda x: x["kind"] == "song", json_response),
                    )
                )
            )

        self.database.insert_album_art(artist_name, self.format_json(urls))

        return self.format_json(urls)

    @staticmethod
    def format_json(tuple_list: list):
        d = []
        for tup in tuple_list:
            b = {"title": tup[0], "url": tup[1]}
            d.append(b)
        return json.dumps(d)
