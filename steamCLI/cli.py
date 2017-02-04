from argparse import ArgumentParser

from steamCLI.config import Config
from steamCLI.steamapp import SteamApp
from steamCLI.results import Results


def main():
    results = Results(max_chars=79)
    config = Config('steamCLI', 'resources.ini')
    app_list = config.get_value('SteamAPIs', 'applist')

    parser = _create_parser(config)
    args = parser.parse_args()

    app = SteamApp(config=config)
    # Title and id are required, but mutually exclusive -> we can do if else
    if args.title:
        app_title = None
        while not app_title:
            # Shell eats up special characters such as ', &, etc.
            app_title = input("Enter title: ").strip()
        print("Gathering price information...")
        app.find_app(origin=app_list, region=args.region, title=app_title)
    else:
        print("Gathering price information...")
        app.find_app(origin=app_list, region=args.region, app_id=args.appid)

    results.format_steam_info(app)
    if args.description:
        results.format_description(app)

    if app.appID:
        if args.scores:
            print("Scraping reviews...")
            app.scrape_app_page()
            results.format_steam_website_info(app)

        if args.historical_low:
            print("Leafing through history books...")
            app.extract_historical_low(args.region)
            results.format_historical_low(app)

        results.print_results()

    else:
        print("Application was not found. Is the supplied information correct?")


def _create_parser(config: Config) -> ArgumentParser:
    """
    Initializes parser with values from a config file.
    """

    app_description = config.get_value('HelpText', 'app_help')
    default_region = config.get_value('SteamRegions', 'default')
    regions = config.get_value('SteamRegions', 'regions').split(',')

    parser = ArgumentParser(description=app_description)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--title", action="store_true",
                       help=config.get_value('HelpText', 'title_help'))
    group.add_argument("-id", "--appid", type=int, action="store",
                       help=config.get_value('HelpText', 'id_help', ),
                       metavar="val")

    parser.add_argument("-d", "--description", action="store_true",
                        help=config.get_value('HelpText', 'desc_help'))
    parser.add_argument("-s", "--scores", action="store_true",
                        help=config.get_value('HelpText', 'reviews_help')),
    parser.add_argument("-r", "--region", action="store", metavar="val",
                        type=str.lower, default=default_region, choices=regions,
                        help=config.get_value('HelpText', 'region_help') +
                        ' Available values: ' + ", ".join(regions))
    parser.add_argument("-l", "--historical_low", action="store_true",
                        help=config.get_value('HelpText', 'historical_help'))

    return parser
