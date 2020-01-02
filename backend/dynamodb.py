import boto3
from os import environ
from boto3_type_annotations.dynamodb import Client

"""
Dynamodb Structure:

Tables: 
    - Lyrics
        - Lyrics grouped by albums keyed with the artist
        - Struct:
            Artist | Song | Lyrics
    - Album Art
        - Url for all album art by an artist.
        - Struct:
            Artist | Url

"""


class DynamoDB:
    def __init__(self):
        self.dynamo: Client = boto3.client(
            "dynamodb",  # , endpoint_url="http://localhost:8000"
            aws_access_key_id=environ.get("AWS_CLIENT_ID", ""),
            aws_secret_access_key=environ.get("AWS_CLIENT_SECRET", ""),
        )
        self.lyrics_table_name = "LYRICS"
        self.album_art_table_name = "ALBUMART"

        self._create_tables_if_not_there()

    def _create_tables_if_not_there(self):
        """
        Creates all the necessary tables.
        :return: None
        """

        # -- Create "lyrics" Table --
        try:
            response = self.dynamo.create_table(
                KeySchema=[
                    {"AttributeName": "Track", "KeyType": "HASH"},
                    {"AttributeName": "Artist", "KeyType": "RANGE"},
                ],
                TableName=self.lyrics_table_name,
                AttributeDefinitions=[
                    {"AttributeName": "Artist", "AttributeType": "S"},
                    {"AttributeName": "Track", "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10,
                },
            )
            print(response)
            waiter = self.dynamo.get_waiter("table_exists")
            waiter.wait(TableName=self.lyrics_table_name)
            print("Exists Now")
        except self.dynamo.exceptions.ResourceInUseException as e:
            print(e)

        # -- Create AlbumArt Table --
        try:
            response = self.dynamo.create_table(
                AttributeDefinitions=[
                    {"AttributeName": "Artist", "AttributeType": "S"}
                ],
                KeySchema=[{"AttributeName": "Artist", "KeyType": "HASH"}],
                TableName=self.album_art_table_name,
                ProvisionedThroughput={
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10,
                },
            )
        except self.dynamo.exceptions.ResourceInUseException as e:
            pass

    def _check_if_item_exists(
        self, table_name: str, key: str, value: str, key2: str, value2: str
    ):
        try:
            item = self.dynamo.get_item(
                TableName=table_name, Key={key: {"S": value}, key2: {"S": value2}}
            )
        except Exception as nf:
            return False
        return True

    def _check_if_item_exists_small(self, table_name: str, key: str, value: str):
        try:
            item = self.dynamo.get_item(TableName=table_name, Key={key: {"S": value}})
        except Exception as nf:
            return False
        return True

    def insert_lyrics(self, artist_name: str, track: str, lyrics: str):
        if artist_name == "" or track == "" or lyrics == "":
            return
        if not self._check_if_item_exists(
            table_name=self.lyrics_table_name,
            key="Artist",
            value=artist_name.lower(),
            key2="Track",
            value2=track.lower(),
        ):
            self.dynamo.put_item(
                TableName=self.lyrics_table_name,
                Item={
                    "Artist": {"S": artist_name.lower()},
                    "Track": {"S": track.lower()},
                    "Lyrics": {"S": lyrics},
                },
            )
        else:
            self.dynamo.update_item(
                TableName=self.lyrics_table_name,
                Key={
                    "Artist": {"S": artist_name.lower()},
                    "Track": {"S": track.lower()},
                },
                AttributeUpdates={"Lyrics": {"Value": {"S": lyrics}}},
            )

    def get_lyrics(self, artist_name: str, album: str):
        try:
            item = self.dynamo.get_item(
                TableName=self.lyrics_table_name,
                Key={
                    "Artist": {"S": artist_name.lower()},
                    "Track": {"S": album.lower()},
                },
            )
        except Exception as db:
            return None

        return (
            item.get("Item", {"Lyrics": {"S": None}})
            .get("Lyrics", {"S": None})
            .get("S")
        )

    def get_album_art(self, artist_name: str):
        try:
            item = self.dynamo.get_item(
                TableName=self.album_art_table_name,
                Key={"Artist": {"S": artist_name.lower()}},
            )
            return item["Item"]["json"]["S"]
        except Exception as db:
            return None

    def insert_album_art(self, artist, json):
        if artist == "" or json == "":
            return
        if not self._check_if_item_exists_small(
            table_name=self.album_art_table_name, key="Artist", value=artist.lower()
        ):
            self.dynamo.put_item(
                TableName=self.album_art_table_name,
                Item={"Artist": {"S": artist.lower()}, "json": {"S": json}},
            )
        else:
            self.dynamo.update_item(
                TableName=self.album_art_table_name,
                Key={"Artist": {"S": artist.lower()}},
                AttributeUpdates={"json": {"Value": {"S": json}}},
            )
