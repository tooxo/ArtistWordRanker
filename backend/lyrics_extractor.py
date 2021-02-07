import re

import api_commons.genius as genius

from typing import List

from backend.lyrics_cleanup import LyricsCleanup

acceptable_codes = [200, 301, 302]


class LyricsExtractor:
    @staticmethod
    async def extract_from_genius_lib(song_name: str, artist: str):
        try:
            genius_api = genius.GeniusApiAsync()
            search_results: List[
                genius.SearchResult] = await genius_api.search_genius(
                re.sub(r"\(.+\)", string=song_name, repl="")
                + " "
                + re.sub(r"\(.+\)", string=artist, repl="")
            )
            search_results = list(
                filter(lambda x: x.url.endswith("lyrics"), search_results)
            )
            assert len(search_results) > 0
            search_result: genius.SearchResult = search_results[0]
            song: genius.Lyrics = await search_result.to_lyrics_async(
                load_annotations=False)
            return song_name, artist, LyricsCleanup.clean_up(song.lyrics_str)
        except Exception:
            print(song_name, artist, "FAILED")
            return song_name, artist, None
