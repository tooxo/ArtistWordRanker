import sqlite3
import aiosqlite

"""
SQLITE JOBS STRUCTURE

ID | LYRICS_GATHERING_STEPS | LYRICS_GATHERING_ALL | LYRICS_GATHERING_DONE | 
DONE | URL
TEXT | INTEGER               | INTEGER              | TEXT (TRUE/FALSE) | 
TEXT (TRUE/FALSE) | TEXT
"""


class SQLite:
    def __init__(self, database):
        self.database: aiosqlite.Connection = database

    @classmethod
    async def create(cls):
        database: aiosqlite.Connection = await aiosqlite.connect("jobs.db")
        await SQLite.initiate_database(database)
        return cls(database)

    @staticmethod
    async def initiate_database(database):
        try:
            c = await database.cursor()
            await c.execute(
                "CREATE TABLE jobs (ID TEXT, LYRICS_GATHERING_STEPS INTEGER, "
                "LYRICS_GATHERING_ALL INTEGER, LYRICS_GATHERING_DONE TEXT, "
                "DONE TEXT, URL TEXT)"
            )
        except sqlite3.OperationalError:
            c = await database.cursor()
            await c.execute("DELETE FROM jobs;")
            # await c.execute("VACUUM;")
            # await database.execute("VACUUM;")

    async def add_job(self, job_id: str):
        c = await self.database.cursor()
        await c.execute(
            "INSERT INTO jobs(ID, LYRICS_GATHERING_STEPS, "
            "LYRICS_GATHERING_ALL, LYRICS_GATHERING_DONE, DONE, URL) "
            "VALUES ('" + job_id + "', 0, 0, 'FALSE', 'FALSE', '')"
        )

    async def edit_lyrics(
        self, job_id: str, step: int, _all: int = None, done: bool = False
    ):
        c = await self.database.cursor()
        if done:
            await c.execute(
                "UPDATE jobs SET LYRICS_GATHERING_DONE = 'TRUE' WHERE ID = '"
                + job_id
                + "'"
            )
            return

        if _all is not None:
            await c.execute(
                "UPDATE jobs SET LYRICS_GATHERING_ALL = " + str(_all) + ","
                                                                        "LYRICS_GATHERING_STEPS = "
                + str(step)
                + " WHERE ID='"
                + job_id
                + "'"
            )
            return

        await c.execute(
            "UPDATE jobs SET LYRICS_GATHERING_STEPS = " + str(step) + " WHERE "
                                                                      "ID='"
            + job_id + "'"
        )

    async def increase_lyrics(self, job_id):
        c = await self.database.cursor()
        await c.execute(
            "UPDATE jobs SET LYRICS_GATHERING_STEPS = LYRICS_GATHERING_STEPS "
            "+ 1 WHERE ID ='"
            + job_id
            + "'"
        )

    async def set_done(self, job_id: str, url: str):
        c = await self.database.cursor()
        await c.execute(
            "UPDATE jobs SET done='TRUE', URL='"
            + url
            + "' WHERE ID='"
            + job_id
            + "'"
        )

    async def get_job(self, job_id: str):
        c = await self.database.cursor()
        await c.execute("SELECT * FROM jobs WHERE ID=?", (job_id,))
        rows = list(await c.fetchall())
        return {
            "ID": rows[0][0],
            "LYRICS_GATHERING_STEPS": rows[0][1],
            "LYRICS_GATHERING_ALL": rows[0][2],
            "LYRICS_GATHERING_DONE": rows[0][3],
            "DONE": rows[0][4],
            "URL": rows[0][5],
        }
