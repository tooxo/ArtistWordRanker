from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import json
from backend.dynamodb import DynamoDB


class AlbumArt:
    def __init__(self):
        self.base_url = "https://www.covermytunes.com/search.php?search_query="
        self.dynamo = DynamoDB()

    def get_artist(self, artist_name):
        temp = self.dynamo.get_album_art(artist_name)
        if temp is not None:
            return temp
        urls = []
        with requests.get(self.base_url + quote(artist_name), verify=False) as g:
            soup = BeautifulSoup(g.text, "html.parser")
            divs = soup.find_all("div", {"class": "ProductImage"})
            for possible_image in divs:
                description = possible_image.findChildren("a", recursive=True)
                image = possible_image.findChildren("img", recursive=True)
                extraction = (description[0]["title"], image[0]["src"])
                if extraction not in urls:
                    urls.append(extraction)

        self.dynamo.insert_album_art(artist_name, self.format_json(urls))

        return self.format_json(urls)

    @staticmethod
    def format_json(tuple_list: list):
        d = []
        for tup in tuple_list:
            b = {"title": tup[0], "url": tup[1]}
            d.append(b)
        return json.dumps(d)
