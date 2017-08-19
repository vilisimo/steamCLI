import argparse
from argparse import ArgumentParser

from steamCLI.config import Config
from steamCLI.results import Results
from steamCLI.steamapp import SteamApp


def main():
    config = Config('steamCLI', 'resources.ini')
    app_list = config.get_value(section='SteamAPIs', key='applist')
    parser = _create_parser(config)
    args = parser.parse_args()

    app = SteamApp(config=config)
    _retrieve_main_app_info(args=args, app=app, app_list=app_list)

    results = Results(app=app, max_chars=79)
    results.format_steam_info()

    if args.description:
        results.format_description()

    # If app has an ID, we have managed to find it in Steam
    if app.appID:
        if args.scores:
            _add_scores_to_app(app=app, results=results)
        if args.historical_low:
            _add_historical_low(args=args, app=app, results=results)
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


def _retrieve_title() -> str:
    """ Gets title from the user's input """

    app_title = None
    while not app_title:
        # Shell eats up special characters such as ', &, etc.
        app_title = input("Enter title: ").strip()

    return app_title


def _retrieve_main_app_info(args: argparse.Namespace, app: SteamApp, app_list):
    """ 
    Find and update SteamApp object with info about application
     
    :param args: argument object that has user entered args.
    :param app: SteamApp that holds information about a particular app.
    :param app_list: Steam's endpoint that has JSON of all the Steam apps.
    """

    # Title and id are required, but mutually exclusive
    if args.title:
        app_title = _retrieve_title()
        app.find_app(origin=app_list, region=args.region, title=app_title)
    else:
        print("Gathering price information...")
        app.find_app(origin=app_list, region=args.region, app_id=args.appid)


def _add_scores_to_app(app: SteamApp, results: Results):
    """
    Add review scores to a given SteamApp and format associated Results object 
    accordingly.
    """

    print("Scraping reviews...")
    app.scrape_app_page()
    results.format_steam_website_info()


def _add_historical_low(args: argparse.Namespace, app: SteamApp, results: Results):
    """
    Add historical low information to a given SteamApp and format associated 
    Results object accordingly.
    """

    print("Leafing through history books...")
    app.extract_historical_low(args.region)
    results.format_historical_low()

if __name__ == '__main__':
    main()
