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
        print("Gathering price information...")
        app.find_app(origin=app_list, region=args.region, title=app_title)
    else:
        print("Gathering price information...")
        app.find_app(origin=app_list, region=args.region, app_id=args.appid)

    if app.appID:
        if args.scores:
            print("Scraping reviews...")
            app.scrape_app_page()

        if args.historical_low:
            print("Leafing through history books...")
            app.extract_historical_low(args.region)

        _print_application_info(app, args)

    else:
        print("Application was not found. Is the supplied information correct?")


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
    parser.add_argument("-s", "--scores", action="store_true",
                        help=config.get_value('HelpText', 'reviews_help')),
    parser.add_argument("-r", "--region", action="store", metavar="val",
                        type=str.lower, default=default_region, choices=regions,
                        help=config.get_value('HelpText', 'region_help') +
                        ' Available values: ' + ", ".join(regions))
    parser.add_argument("-l", "--historical_low", action="store_true",
                        help=config.get_value('HelpText', 'historical_help'))

    return parser


def _print_application_info(app, args=None, max_chars=79):
    """
    Prints information about the given app.

    :param app: app for which info needs to be printed out.
    :param args: parsed args. Used to determine whether to show info.
    :param max_chars: how many chars there are in a typical line terminal.
    """

    print("\n" + "".center(max_chars, '*'))
    title = app.title
    release_date = app.release_date if app.release_date else "no release date"
    meta = app.metacritic
    initial = round(app.initial_price / 100, 2) if app.initial_price else "N/A"
    current = round(app.final_price / 100, 2) if app.final_price else "N/A"
    currency = app.currency if app.currency else ""
    discount = app.discount

    title = f"*** {title} ({release_date}) ***"
    prices = f"{current} {currency} ({discount}% from {initial} {currency})"
    meta = f"Metacritic score: {meta}"
    print(title.center(max_chars))
    print(prices.center(max_chars))
    print(meta.center(max_chars))

    if args.scores:
        print()
        if not app.overall_count:
            print("No reviews available".center(max_chars))
        if app.overall_count:
            overall_c = app.overall_count
            overall_p = app.overall_percent
            reviews = f"{overall_c} overall reviews ({overall_p} positive)"
            print(reviews.center(max_chars))
        if app.overall_count and not app.recent_count:
            print("No recent reviews available".center(max_chars))
        if app.recent_count:
            recent_c = app.recent_count
            recent_p = app.recent_percent
            reviews = f"{recent_c} recent reviews ({recent_p} positive)"
            print(reviews.center(max_chars))

    if args.historical_low:
        print()
        low = app.historical_low
        cut = app.historical_cut
        shop = app.historical_shop
        h_low = f"Historical low: {low:.2f} {currency} (-{cut}%). Shop: {shop}"
        print(h_low.center(max_chars))

    if args.description:
        description = app.description
        if len(description) < 1:
            print("\n" + "Short description unavailable.".center(max_chars))
        else:
            print("\n" + f"{description}".center(max_chars))

    print("".center(max_chars, "*") + "\n")
