from os import path
import sqlite3
from sqlite3 import Error


class SqLite:

    def __init__(self, database_path):
        self.connection = None
        self.cursor = None
        self.retry_connection(database_path)

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

    def __execute_command(self, command):
        try:
            self.cursor.execute(command)
        except Error as e:
            print(e)

