import os
import re

import api_commons.spotify as spotify
from typing import List


class Spotify:
    def __init__(self):
        self.client_id = os.environ.get("SPOTIFY_CLIENT", "")
        self.client_secret = os.environ.get("SPOTIFY_SECRET", "")
        self.token = ""
        self.spotify = spotify.SpotifyApi(
            client_id=self.client_id, client_secret=self.client_secret
        )

    async def search_artist(self, query: str):
        search_results: List[spotify.Artist] = await spotify.search_async(
            query,
            await self.spotify.get_auth_token_async(),
            search_result_count=10,
            search_type=spotify.SearchType.ARTIST,
        )
        return list(
            map(
                lambda x: {
                    "id": x.id,
                    "name": x.name,
                    "url": x.external_urls.spotify,
                    "image": x.images[0].url if len(x.images) > 0 else None,
                },
                search_results,
            )
        )

    async def _get_albums_from_id(self, artist_id):
        return list(
            map(
                lambda x: x.id,
                filter(
                    lambda y: y.album_type in ["album", "single"],
                    await spotify.Artist.get_albums_by_id_async(
                        artist_id, await self.spotify.get_auth_token_async()
                    ),
                ),
            )
        )

    async def get_album_images(self, artist_id):
        return list(
            map(
                lambda x: (x.name, x.images[0].url),
                filter(
                    lambda y: y.album_type in ["album", "single"]
                              and len(y.images) > 0,
                    await spotify.Artist.get_albums_by_id_async(
                        artist_id, await self.spotify.get_auth_token_async()
                    ),
                ),
            )
        )

    async def get_all_albums(self, artist_id):
        if artist_id is None:
            return None
        albums = await self._get_albums_from_id(artist_id)
        return albums

    async def _get_tracks_from_album(self, album_id):
        return list(
            map(
                lambda x: (x.name, x.artists[0].name),
                (await spotify.Album.from_id_async(
                    album_id, await self.spotify.get_auth_token_async()
                )).tracks,
            )
        )

    @staticmethod
    def strip_remastered(song_title: str):
        """
        Strips the "Remastered - xxxx" from a songs title
        :param song_title:
        :return:
        """
        regx = r" - Remastered( [\d]{1,4})?"
        return re.sub(regx, "", song_title)

    async def get_songs_by_artist(self, artist_id):
        albums = list(
            filter(
                lambda y: y is not None,
                await self.get_all_albums(artist_id)
            )
        )
        track_tracks = []
        for x in albums:
            track_tracks.extend(await self._get_tracks_from_album(x))
        b_song = []
        for song in track_tracks:
            song_t = self.strip_remastered(song[0])
            if (song_t, song[1]) not in b_song:
                b_song.append((song_t, song[1]))
        songs = list(b_song)
        return songs
