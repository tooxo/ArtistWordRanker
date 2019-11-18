import re
from bs4 import BeautifulSoup
from bs4.element import Tag
import requests
import random
from backend.sqlite import SQLite

acceptable_codes = [200, 301, 302]


class LyricsExtractor:
    def __init__(self):
        pass
        self.sqlite = SQLite()

    def extract_random(self, song_name: str, artist: str, job_id: str):
        sqlite = SQLite()
        pool = [
            LyricsExtractor.extract_from_lyrics_wikia,
            LyricsExtractor.extract_from_genius,
        ]
        x = 0
        while x in range(0, 5):
            try:
                value = (song_name, artist, random.choice(pool)(song_name, artist))
                sqlite.increase_lyrics(job_id)
                return value
            except Exception as e:
                pass
            x += 1
        sqlite.increase_lyrics(job_id)
        print(song_name, artist, "FAILED")
        return None, None, None

    @staticmethod
    def extract_from_lyrics_wikia(song_name: str, artist: str):
        song_name = song_name.replace(" ", "_")
        search_query = artist + ":" + song_name
        url = "https://lyrics.fandom.com/wiki/" + search_query
        with requests.get(url=url) as g:
            if g.status_code not in acceptable_codes:
                raise Exception("")
            soup = BeautifulSoup(g.text, "html.parser")
            text: Tag = soup.find("div", {"class", "lyricbox"})
            text: str = str(text).replace('<div class="lyricbox">', "").replace(
                "<br/>", " "
            ).replace("</div>", "").replace("  ", " ")
            return text

    @staticmethod
    def extract_from_genius(song_name: str, artist: str):
        song_name = re.sub("[^A-z0-9 ]", "", song_name).lower()
        artist = re.sub("[^A-z0-9 ]", "", artist).lower()

        song_name = song_name.replace(" ", "-")
        artist = artist.replace(" ", "-")

        base_url = "https://genius.com/"
        search_query = artist + "-" + song_name + "-lyrics"

        url = base_url + search_query

        with requests.get(url=url, timeout=8) as g:
            if g.status_code not in acceptable_codes:
                raise Exception("")
            soup = BeautifulSoup(g.text, "html.parser")
            div = soup.find("div", {"class", "lyrics"})
            text = div.text
            text = re.sub(r"<.+>", "", text)
            text = text.replace("\n", " ")
            pattern = re.compile(r"\[[A-z0-9 ]+\]")
            while re.search(pattern, text) is not None:
                text = re.sub(pattern, "", text)
            while "  " in text:
                text = text.replace("  ", " ")
            return text
