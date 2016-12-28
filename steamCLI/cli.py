import argparse

from steamCLI.config import Config
from steamCLI.steamapp import SteamApp


def main():
    config = Config('steamCLI', 'resources.ini')
    app_list = config.get_value('SteamAPIs', 'applist')

    parser = _create_parser(config)
    args = parser.parse_args()

    app = SteamApp()
    # Title and id are required, but mutually exclusive -> we can do if else
    if args.title:
        app_title = None
        while not app_title:
            # Shell eats up special characters such as ', &, etc.
            app_title = input("Enter title: ").strip()
        print("Gathering information, hold tight...\n")
        app.find_app(origin=app_list, region=args.region, title=app_title)
    else:
        print("Gathering information, hold tight...\n")
        app.find_app(origin=app_list, region=args.region, appid=args.appid)

    if app.appid:
        _print_application_info(app, desc=args.description)
    else:
        print("Application was not found. Is the supplied information correct?")

        # json_data = app._fetch_json(
        #     'http://store.steampowered.com/api/appdetails?appids={}'.format(app.appid))
        # pprint.pprint(json_data)


def _create_parser(config):
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
                        type=str.lower, default=default_region, choices=regions,
                        help=config.get_value('HelpText', 'region_help') +
                        ' Available values: ' + ", ".join(regions))

    return parser


def _print_application_info(app, desc=False, max_chars=79):
    """
    Prints information about the given app.

    :param app: app for which info needs to be printed out.
    :param desc: whether description should be shown.
    :param max_chars: how many chars there are in a typical line terminal.
    """

    title = app.title
    release_date = app.release_date if app.release_date else "no release date"
    meta = app.metascore
    initial = round(app.initial_price / 100, 2) if app.initial_price else "N/A"
    current = round(app.final_price / 100, 2) if app.final_price else "N/A"
    currency = app.currency if app.currency else ""
    discount = app.discount

    title = f"*** {title} ({release_date}) ***"
    prices = f"{current} {currency} ({discount}% of {initial} {currency})"
    meta = f"Metacritic score: {meta}"
    print(title.center(max_chars))
    print(prices.center(max_chars))
    print(meta.center(max_chars))

    if desc:
        description = app.description
        if len(description) < 1:
            print("\nShort description unavailable.".center(max_chars))
        else:
            print(f"\n{description}".center(max_chars))
