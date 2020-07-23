import os
import re
import urllib.parse

from bs4 import BeautifulSoup
from bs4.element import Tag
import requests
import random
from backend.sqlite import SQLite
from backend.lyrics_cleanup import LyricsCleanup

acceptable_codes = [200, 301, 302]


class LyricsExtractor:
    def __init__(self):
        self.sqlite = SQLite()

    def extract_random(self, song_name: str, artist: str, job_id: str):
        sqlite = SQLite()
        if "GENIUS_API_KEY" in os.environ:
            pool = [LyricsExtractor.extract_from_genius_auth]
        else:
            pool = [
                LyricsExtractor.extract_from_lyrics_wikia,
                LyricsExtractor.extract_from_genius,
            ]
        x = 0
        while x in range(0, 2):
            try:
                value = (
                    song_name,
                    artist,
                    LyricsCleanup.clean_up(
                        random.choice(pool)(song_name, artist)
                    ),
                )
                sqlite.increase_lyrics(job_id)
                return value
            except Exception:
                pass
            x += 1
        sqlite.increase_lyrics(job_id)
        print(song_name, artist, "FAILED")
        return song_name, artist, None

    @staticmethod
    def extract_from_lyrics_wikia(song_name: str, artist: str):
        song_name = song_name.replace(" ", "_")
        search_query = artist + ":" + song_name
        url = "https://lyrics.fandom.com/wiki/" + search_query
        with requests.get(url=url) as g:
            if g.status_code not in acceptable_codes:
                raise Exception(
                    str(g.status_code) + "is not in the available codes."
                )
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

    @staticmethod
    def extract_from_genius_auth(song_name: str, artist: str) -> str:
        # search on genius to extract id
        base_url_search = "https://genius.com/api/search/song?q="
        url_search = base_url_search + urllib.parse.quote(
            re.sub(r"\(.+\)", string=song_name, repl="")
            + " "
            + re.sub(r"\(.+\)", string=artist, repl="")
        )
        song_id = None
        with requests.get(url_search) as response_search:
            search = response_search.json()
            for cat in search["response"]["sections"]:
                for item in sorted(
                    cat["hits"],
                    key=lambda i: i["result"]["stats"].get("pageviews", 0),
                    reverse=True,
                ):
                    if item["result"]["url"].endswith("lyrics"):
                        song_id = item["result"]["id"]
                        break

        assert song_id is not None
        base_url_lyrics = f"https://api.genius.com/songs/{song_id}"
        with requests.get(
            base_url_lyrics,
            headers={"Authorization": f"Bearer {os.environ['GENIUS_API_KEY']}"},
        ) as response_lyrics:
            lyrics = response_lyrics.json()["response"]["song"]["lyrics"][
                "dom"
            ]["children"][0]["children"]
            return " ".join(filter(lambda x: isinstance(x, str), lyrics))
