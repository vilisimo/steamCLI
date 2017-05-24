from steamCLI.steamapp import SteamApp


class Results:
    def __init__(self, app: SteamApp, result: list=None, max_chars: int=79):
        self.app = app
        if result is None:
            self.result = []
        else:
            self.result = result
        self.max_chars = max_chars

        self.description = None
        self.site_stats = None
        self.steam = None
        self.itad = None

    def format_steam_info(self):
        """
        Formats information that was gathered from Steam API.

        :return: formatted string.
        """

        release = (self.app.release_date if self.app.release_date
                   else 'no release date')
        initial = (round(self.app.initial_price / 100, 2)
                   if self.app.initial_price else 'N/A')
        current = (round(self.app.final_price / 100, 2) if self.app.final_price
                   else 'N/A')
        currency = f' {self.app.currency}' if self.app.currency else ''

        self.steam = list()
        self.steam.append(f'*** {self.app.title} ({release}) ***')
        self.steam.append(f'{current}{currency} ({self.app.discount}% '
                          f'from {initial}{currency})')
        self.steam.append(f'Metacritic score: {self.app.metacritic}')

    def format_steam_website_info(self):
        """
        Formats information that was gathered from Steam website.

        :return: formatted string.
        """

        self.site_stats = list()

        if self.app.overall_count:
            self.site_stats.append(f'{self.app.overall_count} overall reviews '
                                   f'({self.app.overall_percent} positive)')
        else:
            self.site_stats.append("No overall reviews available")

        # It makes sense to show absence of recent reviews only if overall
        # reviews are missing as well.
        if self.app.overall_count and not self.app.recent_count:
            self.site_stats.append("No recent reviews available")

        if self.app.recent_count:
            self.site_stats.append(f'{self.app.recent_count} recent reviews '
                                   f'({self.app.recent_percent} positive)')

    def format_historical_low(self):
        """
        Formats information on historical low prices of the given application.

        :return: formatted string.
        """

        lowest = (f'{self.app.historical_low:.2f}' if self.app.historical_low
                  else 'N/A')
        currency = f' {self.app.currency}' if self.app.currency else ''
        cut = self.app.historical_cut if self.app.historical_cut else 'N/A'
        shop = self.app.historical_shop if self.app.historical_shop else 'N/A'

        self.itad = list()
        self.itad.append(f'Historical low: {lowest}{currency} (-{cut}%)')
        self.itad.append(f'Shop: {shop}')

    def format_description(self) -> str:
        """
        Formats given application's description.

        :return: formatted string.
        """

        if self.app.description:
            self.description = self.app.description
        else:
            self.description = 'Short description unavailable'

        return self._center_text([self.description])

    def print_results(self):
        print('\n', ''.center(self.max_chars, '*') + '\n')
        print(self._center_text(self.steam))

        if self.site_stats:
            print('\n', self._center_text(self.site_stats))
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
