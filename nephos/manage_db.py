"""
Manages all the database operations
"""
import os
from contextlib import contextmanager
from logging import getLogger
import sqlite3
from sqlite3 import Error
from .exceptions import DBException
from . import __nephos_dir__


LOG = getLogger(__name__)
DB_PATH = os.path.join(__nephos_dir__, "databases/storage.db")
DB_JOBS_PATH = os.path.join(__nephos_dir__, "databases/jobs.db")


# indexes for channel and share list
CH_NAME_INDEX = 1
CH_IP_INDEX = 2
CH_COUN_INDEX = 3
CH_LANG_INDEX = 4
CH_TMZ_INDEX = 5
CH_STAT_INDEX = 6
SL_MAIL_INDEX = 1
SL_CH_INDEX = 2
SL_COUN_INDEX = 3
SL_LANG_INDEX = 4
SL_TMZ_INDEX = 5


class DBHandler:
    """
    Handles operations related to database; insertion, updating and deletion.
    """

    def first_time(self):
        """
        Initialise the database with important tables
            Channels:
                Stores the list of channels

        Returns
        -------

        """
        LOG.debug("Initialising database at %s", DB_PATH)

        with self.connect() as db_cur:

            # create channels and share_list table
            # multiple values to be separated by space. Eg. "AUS IND" for AUS and IND
            # country channels to be shared
            db_cur.execute("""CREATE TABLE IF NOT EXISTS channels (
                                    channel_id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    ip text NOT NULL,
                                    country_code text,
                                    lang text,
                                    timezone text NOT NULL,
                                    status text DEFAULT "up"
                                    );

            """)

            db_cur.execute("""CREATE TABLE IF NOT EXISTS share_list (
                                    share_id integer PRIMARY KEY,
                                    email text,
                                    channel_name text,
                                    country_code text,
                                    lang text,
                                    timezone text,
                                    FOREIGN KEY (channel_name) REFERENCES channels(name)
                                    );
            """)

            # indexing columns
            db_cur.execute("""CREATE UNIQUE INDEX indexed_name ON channels(
                                    ip
                                    );                             
            """)

            db_cur.execute("""CREATE UNIQUE INDEX indexed_email ON share_list(
                                    email
                                    );   
            """)

    @staticmethod
    def insert_data(db_cur, table_name, row_data):
        """
        Inserts data into tables

        Parameters
        ----------
        db_cur
            cursor to database
        table_name
            type: str
            name of the table to which the data is to be inserted
        row_data
            type: dict
            containing the key-value paired row data to be appended

        Returns
        -------
        id
            type: int
            the channel_id/share_id of the new data

        """
        cols = ', '.join('{}'.format(col) for col in row_data.keys())
        vals = ', '.join("'{}'".format(col) for col in row_data.values())
        try:
            command = """INSERT INTO "{table_name}"
                            ({keys}) 
                            VALUES ({values})""".format(table_name=table_name, keys=cols,
                                                        values=vals)
            db_cur.execute(command)
            return db_cur.lastrowid
        except Error as err:
            LOG.warning("Failed to insert %s into %s", row_data, table_name)
            LOG.debug(err)

    @staticmethod
    def init_jobs_db():
        """
        creates the job database file

        Returns
        -------

        """
        try:
            conn = sqlite3.connect(DB_JOBS_PATH)
            conn.close()
        except Error as error:
            LOG.warning("Unable to connect to jobs database!\nPlease look into debugging details.")
            LOG.debug(error)
            # catch this exception only if the error can be ignored.
            raise DBException("Database Operation failed!")

    @staticmethod
    @contextmanager
    def connect():
        """
        Instantiates the class with a connection to the main database which stores
        channels and share lists.
        Provides cursor to the database connection.

        """
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            yield conn.cursor()
            conn.commit()
            conn.close()
        except Error as error:
            LOG.warning("Unable to connect to database!\nPlease look into debugging details.")
            LOG.debug(error)
            # catch this exception only if the error can be ignored.
            raise DBException("Database Operation failed!")
