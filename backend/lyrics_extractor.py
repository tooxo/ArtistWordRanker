import re

import api_commons.genius as genius

from typing import List

from backend.sqlite import SQLite
from backend.lyrics_cleanup import LyricsCleanup

acceptable_codes = [200, 301, 302]


class LyricsExtractor:
    def __init__(self):
        self.sqlite = SQLite()

    @staticmethod
    def extract_random(song_name: str, artist: str, job_id: str):
        sqlite = SQLite()
        x = 0
        while x in range(0, 1):
            try:
                value = (
                    song_name,
                    artist,
                    LyricsCleanup.clean_up(
                        LyricsExtractor.extract_from_genius_lib(
                            song_name, artist
                        )
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
    def extract_from_genius_lib(song_name: str, artist: str):
        genius_api = genius.GeniusApi()
        search_results: List[genius.SearchResult] = genius_api.search_genius(
            re.sub(r"\(.+\)", string=song_name, repl="")
            + " "
            + re.sub(r"\(.+\)", string=artist, repl="")
        )
        search_results = list(
            filter(lambda x: x.url.endswith("lyrics"), search_results)
        )
        assert len(search_results) > 0
        search_result: genius.SearchResult = search_results[0]
        song: genius.Lyrics = search_result.to_lyrics(load_annotations=False)
        return song.lyrics_str
