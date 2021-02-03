import requests
import time
import base64
import threading
import multiprocessing.pool
import requests_cache
import os
import re

import api_commons.spotify as spotify
from typing import List

requests_cache.install_cache("requests.cache")


class Spotify:
    def __init__(self):
        self.client_id = os.environ.get("SPOTIFY_CLIENT", "")
        self.client_secret = os.environ.get("SPOTIFY_SECRET", "")
        self.token = ""
        self.spotify = spotify.SpotifyApi(
            client_id=self.client_id, client_secret=self.client_secret
        )

    def _invalidate_token(self):
        if self.token != "":
            for x in range(1, 3000):
                try:
                    time.sleep(x)
                except InterruptedError:
                    self.token = ""
                    break
            self.token = ""

    def _request_token(self):
        if self.token == "":
            string = self.client_id + ":" + self.client_secret
            enc = base64.b64encode(string.encode())
            url = "https://accounts.spotify.com/api/token"
            header = {
                "Authorization": "Basic " + enc.decode(),
                "Content-Type": "application/x-www-form-urlencoded",
            }
            payload = "grant_type=client_credentials&undefined="
            with requests.post(url=url, headers=header, data=payload) as p:
                self.token = p.json().get("access_token")
            threading.Thread(target=self._invalidate_token).start()
            return self.token
        else:
            return self.token

    def research_artist(self, artist_name):
        artists: List[spotify.Artist] = spotify.search(
            artist_name,
            token=self.spotify.get_auth_token(),
            search_result_count=5,
            search_type=spotify.SearchType.ARTIST,
        )
        if len(artists) == 0:
            return None
        return sorted(artists, key=lambda x: x.followers, reverse=True)[0].id

    def search_artist(self, query: str):
        search_results: List[spotify.Artist] = spotify.search(
            query,
            self.spotify.get_auth_token(),
            search_result_count=10,
            search_type=spotify.SearchType.ARTIST,
        )
        return list(
            map(
                lambda x: {
                    "name": x.name,
                    "url": x.external_urls.spotify,
                    "image": x.images[0].url if len(x.images) > 0 else None,
                },
                search_results,
            )
        )

    def _get_albums_from_id(self, artist_id):
        return list(
            map(
                lambda x: x.id,
                filter(
                    lambda y: y.album_type in ["album", "single"],
                    spotify.Artist.get_albums_by_id(
                        artist_id, self.spotify.get_auth_token()
                    ),
                ),
            )
        )

    def get_album_images(self, artist_name):
        if artist_name == "":
            return None
        artist_id = self.research_artist(artist_name)
        if artist_id is None:
            return None
        return list(
            map(
                lambda x: (x.name, x.images[0].url),
                filter(
                    lambda y: y.album_type in ["album", "single"]
                    and len(y.images) > 0,
                    spotify.Artist.get_albums_by_id(
                        artist_id, self.spotify.get_auth_token()
                    ),
                ),
            )
        )

    def get_all_albums(self, artist_name):
        if artist_name == "":
            return None
        artist_id = self.research_artist(artist_name)
        if artist_id is None:
            return None
        albums = self._get_albums_from_id(artist_id)
        return albums

    def _get_tracks_from_album(self, album_id):
        return list(
            map(
                lambda x: (x.name, x.artists[0].name),
                spotify.Album.from_id(
                    album_id, self.spotify.get_auth_token()
                ).tracks,
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

    def get_songs_by_artist(self, artist_name):
        songs = []
        albums = self.get_all_albums(artist_name)
        pool = multiprocessing.pool.ThreadPool(processes=3)
        _als = []
        if albums is not None:
            for album in albums:
                if album is not None:
                    _als.append(album)
        track_tracks = pool.map(self._get_tracks_from_album, _als)
        for track_list in track_tracks:
            songs += track_list
        b_song = []
        for song in songs:
            song_t = self.strip_remastered(song[0])
            if (song_t, song[1]) not in b_song:
                b_song.append((song_t, song[1]))
        songs = list(b_song)
        return songs
