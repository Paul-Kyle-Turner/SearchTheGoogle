# Python 3.7
# Paul Turner - turnerp5@students.rowan.edu
# September 4 2019

import json
import datetime
from googleapiclient.discovery import build
from dbSQLiteGoog import SqLiteGoog
from dbSQLiteGoog import SqLite
from sqlite3 import Error


class GoogleApp:

    def __init__(self, key, engine, custom_search_version, num_search,
                 text_filename, json_filename, database_path,
                 json_output, text_output, db_output,
                 tables=None, goog=True):
        # set arguments that are needed
        self.engine = engine
        self.num_search = num_search
        self.text_filename = text_filename
        self.json_filename = json_filename
        self.database_path = database_path
        self.json_output = json_output
        self.text_output = text_output
        self.db_output = db_output
        if db_output and database_path is not None:
            if tables is not None and goog is not True:
                # use a different SqLite database set up
                # this will require all commands to go through the execute command method
                self.db = self.sql_db_setup_custom(SqLite, database_path, tables)
            elif tables is not None and goog:
                # use different tables then the three defaults
                # warning this can have unintended effects on the default use of SqLiteGoog
                self.db = self.sql_db_setup_custom(SqLiteGoog, database_path, tables)
            else:
                self.db = self.sql_db_setup(SqLiteGoog, database_path)
        # create the resources for the search engine
        try:
            self.service = build('customsearch', custom_search_version, developerKey=key)
            self.resource = self.service.cse()
        except ConnectionError as e:
            print(e)

    def search(self, query):
        result = self.resource.list(q=query, cx=self.engine, num=self.num_search).execute()
        return result

    def to_output(self, result):
        if not self.json_output and not self.db_output:
            self.text_output = True
        if self.json_output:
            self.to_text_file(result)
        if self.text_output:
            self.to_text_file(result)
        if self.db_output:
            self.to_sql_db(result)

    def to_text_file(self, result):
        with open(self.text_filename, 'w', encoding="utf-8") as file:
            request_info = result['queries']['request'][0]
            date = datetime.datetime.now().strftime("%c")
            file.write("Search Terms: {}\n".format(request_info['searchTerms']))
            file.write("Result Count: {}\n".format(request_info['totalResults']))
            file.write("Timestamp: {}\n\n".format(date))

        # Write search results to file
        items = result['items']
        with open(self.text_filename, 'a', encoding="utf-8") as file:
            for counter, item in enumerate(items):
                file.write("Item #{}\n".format(counter + 1))
                file.write("Title: {}\n".format(item['title']))
                file.write("Snippet: {}\n".format(item['snippet']))
                file.write("Link: {}\n\n".format(item['link']))

    def to_json_file(self, result):
        with open(self.json_filename, 'w') as file:
            json.dump(result, file)

    def sql_db_setup(self, sql_class, database_path):
        try:
            self.db = sql_class(database_path)
        except Error as e:
            print(e)
            self.db = None
        return self.db

    def sql_db_setup_custom(self, sql_class, database_path, tables):
        try:
            self.db = sql_class(tables, database_path)
        except Error as e:
            print(e)
            self.db = None
        return self.db

    def to_sql_db(self, result, tables=None):
        if self.db is None and tables is not None:
            print("Setup database")
        if self.db is None:
            print("DB NONE")

    def get_engine(self):
        return self.engine

    def set_engine(self, engine):
        self.engine = engine

    def get_num_search(self):
        return self.num_search

    def set_num_search(self, num_search):
        self.num_search = num_search

    def get_text_filename(self):
        return self.text_filename

    def set_text_filename(self, text_filename):
        self.text_filename = text_filename

    def get_json_filename(self):
        return self.json_filename

    def set_json_filename(self, json_filename):
        self.json_filename = json_filename

    def get_database_path(self):
        return self.database_path

    def set_database_path(self, database_path):
        self.database_path = database_path

    def get_json_output(self):
        return self.json_output

    def set_json_output(self, json_output):
        self.json_output = json_output

    def get_text_output(self):
        return self.json_output

    def set_text_output(self, text_output):
        self.text_output = text_output

    def get_db_output(self):
        return self.db_output

    def set_db_output(self, db_output):
        self.db_output = db_output

    engine = property(get_engine, set_engine)
    num_search = property(get_num_search, set_num_search)
    text_filename = property(get_text_filename, set_text_filename)
    json_filename = property(get_json_filename, set_json_filename)
    database_path = property(get_database_path, set_database_path)
    json_output = property(get_json_output, set_json_output)
    text_output = property(get_text_output, set_text_output)
    db_output = property(get_db_output, set_db_output)



