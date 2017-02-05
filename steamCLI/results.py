from steamCLI.steamapp import SteamApp


class Results:
    def __init__(self, result: list=None, max_chars: int=79):
        if result is None:
            self.result = []
        else:
            self.result = result
        self.max_chars = max_chars

        self.description = None
        self.website = None
        self.steam = None
        self.itad = None

    def format_steam_info(self, app: SteamApp):
        """
        Formats information that was gathered from Steam API.

        :param app: steam application from which info has to be formatted.
        :return: formatted string.
        """

        rel_date = app.release_date if app.release_date else 'no release date'
        initial = (round(app.initial_price / 100, 2) if app.initial_price
                   else 'N/A')
        current = (round(app.final_price / 100, 2) if app.final_price
                   else 'N/A')
        currency = f' {app.currency}' if app.currency else ''

        self.steam = list()
        self.steam.append(f'*** {app.title} ({rel_date}) ***')
        self.steam.append(f'{current}{currency} ({app.discount}% '
                          f'from {initial}{currency})')
        self.steam.append(f'Metacritic score: {app.metacritic}')

    def format_steam_website_info(self, app: SteamApp):
        """
        Formats information that was gathered from Steam website.

        :param app: steam application from which info has to be formatted.
        :return: formatted string.
        """

        self.website = list()

        if app.overall_count:
            self.website.append(f'{app.overall_count} overall reviews '
                                f'({app.overall_percent} positive)')
        else:
            self.website.append("No overall reviews available")

        # It makes sense to show absence of recent reviews only if overall
        # reviews are missing as well.
        if app.overall_count and not app.recent_count:
            self.website.append("No recent reviews available")

        if app.recent_count:
            self.website.append(f'{app.recent_count} recent reviews '
                                f'({app.recent_percent} positive)')

    def format_historical_low(self, app: SteamApp):
        """
        Formats information on historical low prices of the given application.

        :param app: steam application from which info has to be formatted.
        :return: formatted string.
        """

        lowest = f'{app.historical_low:.2f}' if app.historical_low else 'N/A'
        currency = f' {app.currency}' if app.currency else ''
        cut = app.historical_cut if app.historical_cut else 'N/A'
        shop = app.historical_shop if app.historical_shop else 'N/A'

        self.itad = list()
        self.itad.append(f'Historical low: {lowest}{currency} (-{cut}%)')
        self.itad.append(f'Shop: {shop}')

    def format_description(self, app: SteamApp) -> str:
        """
        Formats given application's description.

        :param app: steam application from which info has to be formatted.
        :return: formatted string.
        """

        if app.description:
            self.description = app.description
        else:
            self.description = 'Short description unavailable'

        return self._center_text([self.description])

    def print_results(self):
        print('\n', ''.center(self.max_chars, '*') + '\n')
        print(self._center_text(self.steam))

        if self.website:
            print('\n', self._center_text(self.website))
        if self.itad:
            print('\n', self._center_text(self.itad))
        if self.description:
            print('\n', self.description.center(self.max_chars))

        print('\n', ''.center(self.max_chars, '*') + '\n')

    def _center_text(self, text: list) -> str:
        """
        Helper method that centers given text.

        :param text: list with string values that need to be centered.
        :return: centered string.
        """

        return '\n'.join(line.center(self.max_chars) for line in text)
