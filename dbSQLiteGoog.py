from os import path
import sqlite3
from sqlite3 import Error


class SqLite:

    def __init__(self, database_path, tables):
        self.connection = None
        self.cursor = None
        self.retry_connection(database_path)
        self.__create_tables(tables)

    def retry_connection(self, database_path):
        if path.exists(database_path):
            self.connection = None
            try:
                self.connection = sqlite3.connect(database_path)
            except ConnectionError as e:
                print(e)
            if self.connection is not None:
                self.cursor = self.connection.cursor()
        else:
            print("Failed to find db!")

    def __create_tables(self, tables):
        for table in tables:
            try:
                self.cursor.execute(table)
            except Error as e:
                print(e)

