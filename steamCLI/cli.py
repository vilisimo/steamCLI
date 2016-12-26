import argparse

from steamCLI.config import Config
from steamCLI.steamapp import SteamApp


def create_parser(config):
    """
    Initializes parser with values from a config file.
    """

    app_description = config.get_value('HelpText', 'app_help')
    default_region = config.get_value('SteamRegions', 'default')
    regions = config.get_value('SteamRegions', 'regions').split(',')

    parser = argparse.ArgumentParser(description=app_description)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--title", action="store_true",
                       help=config.get_value('HelpText', 'title_help'))
    group.add_argument("-id", "--appid", type=int, action="store",
                       help=config.get_value('HelpText', 'id_help', ),
                       metavar="val")
    parser.add_argument("-d", "--description", action="store_true",
                        help=config.get_value('HelpText', 'desc_help'))
    parser.add_argument("-r", "--region", action="store", metavar="val", 
                         default=default_region, choices=regions, 
                        help=config.get_value('HelpText', 'region_help') + 
                        ' Available values: ' + ", ".join(regions))
    
    return parser


def main():
    config = Config('steamCLI', 'resources.ini')
    APP_LIST = config.get_value('SteamAPIs', 'applist')
    REGIONS = config.get_value('SteamRegions', 'regions').split(',')

    parser = create_parser(config)

    args = parser.parse_args()
    if args.region and args.region not in REGIONS:
        print("Region not recognized. Default will be used. Available values:\n"
              "'au', 'br', 'ca', 'cn', 'eu1', 'eu2', 'ru', 'tr', 'uk', 'us'")
        print()
        args.region = config.get_value('SteamRegions', 'default')

    app = SteamApp()
    if args.title:
        # Shell eats up special characters, such as ', &, etc. Hence, input().
        app_title = None
        while not app_title:
            app_title = input("Enter title:\t").strip()
        app.title = app_title  # Reassign later, so that capwords are not needed

        print("Gathering information, hold tight...\n")
        app.assign_id(origin=APP_LIST)
        # From here function should be used, as both appid and title will use it
        if app.appid:
            app.assign_json_info()
            values = {
                'title': app.title,
                'release_date': app.release_date,
                'meta': app.metacritic,
                'description': app.description,
                'initial': round(app.initial_price / 100, 2) if
                app.initial_price else "N/A",
                'current': round(app.final_price / 100, 2) if
                app.final_price else "N/A",
                'currency': app.currency if app.currency else "",
                'discount': app.discount,
            }

            # Not the most efficient way, but more readable
            title = "*** {title} ({release_date}) ***".format(**values)
            print(title.center(79))
            prices = "{current} {currency} ({discount}% of {initial} " \
                     "{currency})".format(**values)
            print(prices.center(79))
            meta = "Metacritic score: {meta}".format(**values)
            print(meta.center(79))
            if args.description:
                if len(values['description']) < 1:
                    print("\nShort description unavailable.".center(79))
                else:
                    description = "\n{description}".format(**values)
                    print(description.center(79))
        else:
            print("Application was not found. Make sure the title is correct!")

        # json_data = app._fetch_json(
        #     'http://store.steampowered.com/api/appdetails?appids={}'.format(app.appid))
        # pprint.pprint(json_data)

    elif args.appID:
        app.appid = args.appID
        print(app.appid)
        # json = app._fetch_json(
        #     'http://store.steampowered.com/api/appdetails?appids=11')
        # pprint.pprint(json["11"]['success'])

