import sqlite3

"""
SQLITE JOBS STRUCTURE

ID | LYRICS_GATHERING_STEPS | LYRICS_GATHERING_ALL | LYRICS_GATHERING_DONE | DONE | URL
TEXT | INTEGER               | INTEGER              | TEXT (TRUE/FALSE) | TEXT (TRUE/FALSE) | TEXT
"""


class SQLite:
    def __init__(self):
        self.database = sqlite3.connect("jobs.db")
        # self.initiate_database()

    def initiate_database(self):
        try:
            c = self.database.cursor()
            c.execute(
                "CREATE TABLE jobs (ID TEXT, LYRICS_GATHERING_STEPS INTEGER, "
                "LYRICS_GATHERING_ALL INTEGER, LYRICS_GATHERING_DONE TEXT, DONE TEXT, URL TEXT)"
            )
            self.database.commit()
        except sqlite3.OperationalError:
            c = self.database.cursor()
            c.execute("DELETE FROM jobs;")
            self.database.commit()
            c.execute("VACUUM;")
            self.database.commit()

    def add_job(self, job_id: str):
        c = self.database.cursor()
        c.execute(
            "INSERT INTO jobs(ID, LYRICS_GATHERING_STEPS, LYRICS_GATHERING_ALL, LYRICS_GATHERING_DONE, DONE, URL) "
            "VALUES ('" + job_id + "', 0, 0, 'FALSE', 'FALSE', '')"
        )
        self.database.commit()

    def edit_lyrics(self, job_id: str, step: int, _all: int = None, done: bool = False):
        c = self.database.cursor()
        if done:
            c.execute(
                "UPDATE jobs SET LYRICS_GATHERING_DONE = 'TRUE' WHERE ID = '"
                + job_id
                + "'"
            )
            self.database.commit()
            return

        if _all is not None:
            c.execute(
                "UPDATE jobs SET LYRICS_GATHERING_ALL = " + str(_all) + ","
                "LYRICS_GATHERING_STEPS = " + str(step) + " WHERE ID='" + job_id + "'"
            )
            self.database.commit()
            return

        c.execute(
            "UPDATE jobs SET LYRICS_GATHERING_STEPS = " + str(step) + " WHERE "
            "ID='" + job_id + "'"
        )
        self.database.commit()

    def increase_lyrics(self, job_id):
        c = self.database.cursor()
        c.execute(
            "UPDATE jobs SET LYRICS_GATHERING_STEPS = LYRICS_GATHERING_STEPS + 1 WHERE ID ='"
            + job_id
            + "'"
        )
        self.database.commit()

    def set_done(self, job_id: str, url: str):
        c = self.database.cursor()
        c.execute(
            "UPDATE jobs SET done='TRUE', URL='" + url + "' WHERE ID='" + job_id + "'"
        )
        self.database.commit()

    def get_job(self, job_id: str):
        c = self.database.cursor()
        c.execute("SELECT * FROM jobs WHERE ID=?", (job_id,))
        rows = c.fetchall()

        return {
            "ID": rows[0][0],
            "LYRICS_GATHERING_STEPS": rows[0][1],
            "LYRICS_GATHERING_ALL": rows[0][2],
            "LYRICS_GATHERING_DONE": rows[0][3],
            "DONE": rows[0][4],
            "URL": rows[0][5],
        }
