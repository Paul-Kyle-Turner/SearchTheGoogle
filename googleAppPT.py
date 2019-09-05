# Python 3.7
# Paul Turner - turnerp5@students.rowan.edu
# September 4 2019

import json
import datetime
import argparse
import configparser
from googleapiclient.discovery import build

DEFAULT_CONFIG = 'config.ini'


def to_file(filename, result, json_setting):
    if json_setting:
        with open(filename, 'w') as file:
            json.dump(result, file)
    else:
        with open(filename, 'w', encoding="utf-8") as file:
            request_info = result['queries']['request'][0]
            date = datetime.datetime.now().strftime("%c")

            file.write("Search Terms: {}\n".format(request_info['searchTerms']))
            file.write("Result Count: {}\n".format(request_info['totalResults']))
            file.write("Timestamp: {}\n\n".format(date))

        # Write search results to file
        items = result['items']
        with open(filename, 'a', encoding="utf-8") as file:
            for counter, item in enumerate(items):
                file.write("Item #{}\n".format(counter + 1))
                file.write("Title: {}\n".format(item['title']))
                file.write("Snippet: {}\n".format(item['snippet']))
                file.write("Link: {}\n\n".format(item['link']))


def settings():
    # Argument parser for simple settings changes
    parser = argparse.ArgumentParser()
    parser.add_argument('query', help='Search query')
    parser.add_argument('-c', '--config-file',
                        help='Path to non-default config file')
    parser.add_argument('-e', '--engine',
                        help='Change the default search engine')
    parser.add_argument('-k', '--key',
                        help='Use a different key then the default in config')
    parser.add_argument('-ns', '--num_search',
                        help='Change the default number of search results')
    parser.add_argument('-j', '--json', action='store_true',
                        help='Change the format of the output document to json')
    args = parser.parse_args()

    # Settings configuration, defaults can be changed in the config file
    config = configparser.ConfigParser()
    if args.config_file is None:
        config.read(DEFAULT_CONFIG)
    else:
        config.read(args.config_file)

    if args.config_file is None:
        key = config['DEFAULT']['developerKey']
    else:
        key = args.key

    if args.engine is None:
        engine = config['DEFAULT']['searchEngine']
    else:
        engine = args.engine
    # Setting will be at v1 until version update.  When version updates change to newest version
    custom_search_version = config['DEFAULT']['CSVersion']

    if args.num_search is None:
        num_search = config['DEFAULT']['numSearch']
    else:
        num_search = args.num_search

    if args.json:
        filename = config['DEFAULT']['jsonOutputFile']
    else:
        filename = config['DEFAULT']['outputFile']

    return args, key, engine, custom_search_version, num_search, filename, args.json


def main():
    # Config values
    args, key, engine, custom_search_version, num_search, filename, json_setting = settings()

    # Create google search API
    query = args.query
    service = build('customsearch', custom_search_version, developerKey=key)
    resource = service.cse()

    # Search
    result = resource.list(q=query, cx=engine, num=num_search).execute()

    # Write to either human readable or json dump
    to_file(filename=filename, result=result, json_setting=json_setting)


if __name__ == '__main__':
    main()
