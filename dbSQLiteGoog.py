from os import path
import datetime
import sqlite3
from sqlite3 import Error


class SqLite:

    def __init__(self, database_path):
        self.connection = None
        self.retry_connection(database_path)

    def retry_connection(self, database_path):
        if path.exists(database_path):
            self.connection = None
            try:
                self.connection = sqlite3.connect(database_path)
            except ConnectionError as e:
                print(e)
        else:
            print("Failed to find db!")

    def new_cursor(self):
        try:
            cursor = self.connection.cursor()
        except Error as e:
            print(e)
        return cursor

    def execute_command(self, command, cursor=None):
        try:
            if cursor is None:
                cursor = self.new_cursor()
            cursor.execute(command)
            return cursor
        except Error as e:
            print(e)

    def execute_insert(self, command, variables, cursor=None):
        try:
            if cursor is None:
                cursor = self.new_cursor()
            cursor.execute(command, variables)
            return cursor
        except Error as e:
            print(e)


class SqLiteGoog(SqLite):

    def __init__(self, database_path, tables=None):
        super().__init__(database_path)
        if tables is not None:
            tables = ["""CREATE TABLE IF NOT EXISTS search_term (
                                                        id integer PRIMARY KEY AUTOINCREMENT
                                                        term text NOT NULL
                                                        );""",
                      """CREATE TABLE IF NOT EXISTS url (
                                                        id integer PRIMARY KEY AUTOINCREMENT
                                                        url_snip text NOT NULL
                                                        description text
                                                        FOREIGN KEY (search_term_id) REFERENCES search_term (id)
                                                        );"""
                      """CREATE TABLE IF NOT EXISTS dates (
                                                        id integer PRIMARY KEY AUTOINCREMENT
                                                        date TIMESTAMP
                                                        FOREIGN KEY (url_id) REFERENCES url (id)
                                                        );"""
                      ]
        self.execute_command(tables)

    def select_term_id(self, term):
        row_id = None
        for row in self.execute_command('''SELECT id FROM search_term WHERE term = ?''', term).fetchall():
            row_id = row[0]
        return row_id

    def select_url_id(self, url_snip):
        row_id = None
        for row in self.execute_command('''SELECT id FROM url WHERE url_snip = ?''', url_snip).fetchall():
            row_id = row[0]
        return row_id

    # TERM MUST BE A LIST OF VARIABLES
    def create_search_term(self, term):
        search_term_id = self.select_term_id(term)
        if search_term_id is None:
            cursor = self.execute_insert(''' INSET OR IGNORE INTO search_term(term)
                                        VALUES(?) ''', term)
            return cursor.lastrowid
        else:
            return search_term_id

    # URL MUST BE A LIST OF VARIABLES
    # TERM MUST BE A SEARCH TERM PRIMARY KEY
    def create_url(self, term, url):
        row_id = self.select_url_id(url[1])
        if row_id is not None:
            search_term_id = self.select_term_id(term)
            if search_term_id is not None:
                cursor = self.execute_insert(''' INSERT INTO url(url_snip, description,search_term_id) 
                                        VALUES(?,?,?)''', (url[1], url[2], search_term_id))
                return cursor.lastrowid
        return row_id

    # URL MUST BE A URL PRIMARY KEY
    def create_date(self, url_id, date):
        if date is None:
            date = datetime.datetime.now()
        variables = [date, url_id]
        cursor = self.execute_insert(''' INSERT OR IGNORE INTO dates(date, url)
                                    VALUES(?,?)''', variables)
        return cursor.lastrowid

    def write_result(self, results):
        request_info = results['queries']['request'][0]
        date = datetime.datetime.now().strftime("%c")
        term_id = self.create_search_term(request_info['searchTerms'])
        items = results['items']
        for result in enumerate(items):
            url_id = self.create_url(term_id, result)
            self.create_date(url_id, date)







