import argparse
import pprint

from string import capwords

from steamCLI.config import Config
from steamCLI.steamapp import SteamApp


def main():
    config = Config('steamCLI', 'resources.ini')
    APP_LIST = config.get_value('SteamAPIs', 'applist')

    app_description = config.get_value('HelpText', 'app_help')
    parser = argparse.ArgumentParser(description=app_description)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--title", action="store_true",
                       help=config.get_value('HelpText', 'title_help'))
    group.add_argument("-id", "--appID", type=int, action="store", metavar="",
                       help=config.get_value('HelpText', 'id_help'))
    parser.add_argument("-d", "--description", action="store_true",
                        help=config.get_value('HelpText', 'desc_help'))
    args = parser.parse_args()

    app = SteamApp()
    if args.title:
        # Shell eats up special characters, such as ', &, etc. Hence, input().
        app_title = input("Enter title:\t")
        app.title = app_title  # Reassign later, so that capwords are not needed
        app.assign_id(origin=APP_LIST)
        # From here function should be used, as both appid and title will use it
        print("{} id: {}".format(app.title,
                                 app.appid if app.appid else "Not Found"))
        if app.appid:
            json_data = app._fetch_json(
                'http://store.steampowered.com/api/appdetails?appids={}'.format(app.appid))
            pprint.pprint(json_data)

    elif args.appID:
        app.appid = args.appID
        print(app.appid)
        # json = app._fetch_json(
        #     'http://store.steampowered.com/api/appdetails?appids=11')
        # pprint.pprint(json["11"]['success'])

