import datetime
import sqlite3
from sqlite3 import Error


class SqLite:

    def __init__(self, database_path):
        self.database_path = database_path

    @staticmethod
    def select_row_id(results):
        row_id = None
        for row in results.fetchall():
            row_id = row[0]
        return row_id

    def retry_connection(self, database_path=None):
        if database_path is None:
            database_path = self.database_path
        try:
            connection = sqlite3.connect(database_path)
            return connection
        except ConnectionError as e:
            print(e)

    def execute_command(self, command):
        try:
            connection = self.retry_connection()
            cursor = connection.cursor()
            if cursor is None:
                print("FAILED TO CREATE CURSOR")
            cursor.execute(command)
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(e)

    def execute_command_variables(self, command, variables, rc=False):
        try:
            connection = self.retry_connection()
            cursor = connection.cursor()
            if cursor is None:
                print("FAILED TO CREATE CURSOR")
            cursor.execute(command, variables)
            connection.commit()
            if rc:
                return cursor
            return cursor.lastrowid
        except Error as e:
            print(e)


class SqLiteTwit(SqLite):

    def __init__(self, database_path, tables=None):
        super().__init__(database_path)
        if tables is None:
            tables = ["""CREATE TABLE IF NOT EXISTS screen_name(
                                                        id integer PRIMARY KEY AUTOINCREMENT,
                                                        name TEXT NOT NULL);""",
                      """CREATE TABLE IF NOT  EXISTS timeline(
                                                        id integer PRIMARY KEY AUTOINCREMENT,
                                                        tweet TEXT NOT NULL,
                                                        link TEXT NOT NULL,
                                                        date TIMESTAMP,
                                                        screen_name_id INTEGER NOT NULL,
                                                        FOREIGN KEY (screen_name_id) REFERENCES screen_name(id));""",
                      """CREATE TABLE IF NOT  EXISTS followers(
                                                        id integer PRIMARY KEY AUTOINCREMENT,
                                                        name TEXT NOT NULL,
                                                        screen_name_id INTEGER NOT NULL,
                                                        FOREIGN KEY (screen_name_id) REFERENCES screen_name(id));"""]
        for table in tables:
            self.execute_command(table)

    def select_screen_name_id(self, screen_name):
        results = self.execute_command_variables('''SELECT id FROM screen_name WHERE name = ?;''', [screen_name], rc=True)
        if results is not None:
            return self.select_row_id(results)

    def select_timeline_id(self, tweet):
        results = self.execute_command_variables('''SELECT id FROM timeline WHERE tweet = ?;''', [tweet], rc=True)
        if results is not None:
            return self.select_row_id(results)

    def select_follower_id(self, screen_name):
        results = self.execute_command_variables('''SELECT id FROM followers WHERE name = ?;''', [screen_name], rc=True)
        if results is not None:
            return self.select_row_id(results)

    def create_screen_name(self, screen_name):
        screen_name_id = self.select_screen_name_id(screen_name)
        if screen_name_id is None:
            last_row_id = self.execute_command_variables("""INSERT INTO screen_name(id, name)
                                        VALUES(?,?); """, [None, screen_name])
            return last_row_id
        else:
            return screen_name_id

    def create_timeline(self, tweet, link, date, screen_name_id, screen_name=None):
        timeline_id = self.select_timeline_id(tweet)
        if timeline_id is None:
            if screen_name_id is None and screen_name is not None:
                screen_name_id = self.select_screen_name_id(screen_name)
            last_row_id = self.execute_command_variables("""INSERT INTO timeline
                                                    (id, tweet, link, date, screen_name_id)
                                                    VALUES(?,?,?,?,?);""", [None, tweet, link, date, screen_name_id])
            return last_row_id
        else:
            return timeline_id

    def create_follower(self, name, screen_name_id, screen_name=None):
        follower_id = self.select_follower_id(name)
        if follower_id is None:
            if screen_name_id is None and screen_name is not None:
                screen_name_id = self.select_screen_name_id(screen_name)
            last_row_id = self.execute_command_variables('''INSERT INTO timeline(id, name, screen_name_id)
                                            VALUES(?,?,?);''', [None, name, screen_name_id])
            return last_row_id
        else:
            return follower_id


class SqLiteGoog(SqLite):

    def __init__(self, database_path, tables=None):
        super().__init__(database_path)
        if tables is None:
            tables = ["""CREATE TABLE IF NOT EXISTS search_term (
                                                        id integer PRIMARY KEY AUTOINCREMENT,
                                                        term TEXT NOT NULL
                                                        );""",
                      """CREATE TABLE IF NOT EXISTS url (
                                                        id integer PRIMARY KEY AUTOINCREMENT,
                                                        title text NOT NULL,
                                                        link text NOT NULL,
                                                        description text,
                                                        search_term_id INTEGER NOT NULL,
                                                        FOREIGN KEY (search_term_id) REFERENCES search_term(id)
                                                        );""",
                      """CREATE TABLE IF NOT EXISTS dates (
                                                        id integer PRIMARY KEY AUTOINCREMENT,
                                                        date TIMESTAMP,
                                                        url_id INTEGER NOT NULL,
                                                        FOREIGN KEY (url_id) REFERENCES url(id)
                                                        );"""
                      ]
        for table in tables:
            self.execute_command(table)

    def select_term_id(self, term):
        results = self.execute_command_variables('''SELECT id FROM search_term WHERE term = ?;''', [term], rc=True)
        if results is not None:
            return self.select_row_id(results)

    def select_url_id(self, link):
        results = self.execute_command_variables('''SELECT id FROM url WHERE link = ?;''', [link], rc=True)
        if results is not None:
            return self.select_row_id(results)

    def select_date_id(self, date):
        results = self.execute_command_variables('''SELECT id FROM dates WHERE date = ?;''', [date], rc=True)
        if results is not None:
            return self.select_row_id(results)

    # TERM MUST BE A LIST OF VARIABLES
    def create_search_term(self, term):
        search_term_id = self.select_term_id(term)
        if search_term_id is None:
            last_row_id = self.execute_command_variables('INSERT INTO search_term(id, term) VALUES(?,?);', [None, term])
            return last_row_id
        else:
            return search_term_id

    # URL MUST BE A LIST OF VARIABLES
    # TERM MUST BE A SEARCH TERM PRIMARY KEY
    def create_url(self, term, title, link, description, search_term_id=None):
        row_id = self.select_url_id(link)
        if row_id is None:
            if search_term_id is None:
                search_term_id = self.select_term_id(term)
            if search_term_id is not None:
                last_row_id = self.execute_command_variables(''' INSERT INTO url
                                        (id, title, link, description, search_term_id) 
                                        VALUES(?,?,?,?,?);''', [None, title, link, description, search_term_id])
                return last_row_id
        return row_id

    # URL MUST BE A URL PRIMARY KEY
    def create_date(self, url_id, date=None):
        if date is None:
            date = datetime.datetime.now()
        else:
            date_id = self.select_date_id(date)
            return date_id
        last_row_id = self.execute_command_variables(''' INSERT INTO dates(id, date, url_id)
                                    VALUES(?,?,?);''', [None, date, url_id])
        return last_row_id

    #doesn't work
    def write_result(self, results):
        request_info = results['queries']['request'][0]
        date = datetime.datetime.now().strftime("%c")
        term_id = self.create_search_term(request_info['searchTerms'])

        items = results['items']

        for item in enumerate(items):
            url_id = self.create_url(term_id, item['title'], item['link'], item['snippet'])
            self.create_date(url_id, date)

