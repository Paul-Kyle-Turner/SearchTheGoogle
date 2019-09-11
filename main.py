import argparse
import configparser
from googleAppPT import GoogleApp

DEFAULT_CONFIG = 'config.ini'


def settings(args):
    # Settings configuration, defaults can be changed in the config file
    config = configparser.ConfigParser()
    if args.config_file is None:
        config.read(DEFAULT_CONFIG)
    else:
        config.read(args.config_file)

    # set the search engine key or grab the key from config
    if args.engine is None:
        engine = config['DEFAULT']['customSearchEngine']
    else:
        engine = args.engine

    # set the api key or grab the key from config
    if args.config_file is None or args.key is not None:
        key = config['DEFAULT']['developerKey']
    else:
        key = args.key

    # set the number of search results from either args or config
    if args.num_search is None:
        num_search = config['DEFAULT']['numSearch']
    else:
        num_search = args.num_search

    # Setting will be at v1 until version update.  When version updates change to newest version
    custom_search_version = config['DEFAULT']['CSVersion']

    # set the output files locations
    if args.text is None:
        text_filename = config['DEFAULT']['textOutputFile']
    else:
        text_filename = args.text

    if args.json is None:
        json_filename = config['DEFAULT']['jsonOutputFile']
    else:
        json_filename = args.json

    if args.database is None:
        database_path = config['SQLITE']['databasePath']
    else:
        database_path = args.database

    return key, engine, custom_search_version, num_search, text_filename, json_filename, database_path


def main():
    # Argument parser for simple settings changes
    parser = argparse.ArgumentParser()
    parser.add_argument('query', help='Search query')
    parser.add_argument('-c', '--config_file',
                        help='Path to non-default config file')
    parser.add_argument('-e', '--engine',
                        help='Change the default search engine')
    parser.add_argument('-k', '--key',
                        help='Use a different key then the default in config')
    parser.add_argument('-ns', '--num_search',
                        help='Change the default number of search results')

    parser.add_argument('-j', '--use_json', action='store_true',
                        help='Use a json for the query result')
    parser.add_argument('-jf', '--json',
                        help='Change the json file path')

    parser.add_argument('-ud', '--use_database', action='store_true',
                        help='Use a database for the query result')
    parser.add_argument('-d', '--database',
                        help='set a database path')

    parser.add_argument('-ut', '--use_text', action='store_true',
                        help='Use text for output')
    parser.add_argument('-t', '--text',
                        help='set a database path')
    args = parser.parse_args()

    key, engine, custom_search_version, num_search, text_filename, json_filename, database_path = settings(args)

    # Create the googleApp class for searches
    google = GoogleApp(key, engine, custom_search_version, num_search,
                       text_filename, json_filename, database_path,
                       args.use_json, args.use_text, args.use_database)
    # Run the search
    result = google.search(args.query)
    # Create db object


    # Write the search to file
    google.to_output(result)


if __name__ == '__main__':
    main()