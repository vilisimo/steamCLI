import os
import argparse

from steamCLI.config import Config
from steamCLI.steamapp import SteamApp


def main():
    config = Config('steamCLI', 'resources.ini')
    APP_LIST = config.get_value('SteamAPIs', 'applist')

    parser = argparse.ArgumentParser(description="A command line application to retrieve information on Steam games.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--title", action="store", metavar="",
                       help="title of a game or an app on Steam", nargs="+")
    group.add_argument("-id", "--appID", type=int, action="store", metavar="",
                       help="id of a game or an app on Steam")
    args = parser.parse_args()
    if args.title:
        app_title = " ".join(args.title)  # In case contains multiple words.
        print("Fetching id for '{}'...".format(app_title))
        app = SteamApp(title=app_title)
        app.assign_id(origin=APP_LIST)
        print("{}'s id: {}".format(app.title, app.appid))
    elif args.appID:
        pass