import os
import argparse

from string import capwords

from steamCLI.config import Config
from steamCLI.steamapp import SteamApp


def main():
    config = Config('steamCLI', 'resources.ini')
    APP_LIST = config.get_value('SteamAPIs', 'applist')

    parser = argparse.ArgumentParser(description="A CLI app to retrieve information about Steam apps.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--title", action="store_true",
                       help="title of a game or an app on Steam")
    group.add_argument("-id", "--appID", type=int, action="store", metavar="",
                       help="id of a game or an app on Steam")
    parser.add_argument("-d", "--description", action="store_true",
                        help="include to see the app description")
    args = parser.parse_args()
    if args.title:
        # Shell eats up special characters, such as ', &, etc. Hence, input().
        app_title = input("Enter title:\t")
        app = SteamApp(title=app_title)
        app.assign_id(origin=APP_LIST)
        print("{} id: {}".format(capwords(app.title), 
                                 app.appid if app.appid else "Not Found"))
    elif args.appID:
        pass