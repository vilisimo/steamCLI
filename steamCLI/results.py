from steamCLI.steamapp import SteamApp


class Results:
    def __init__(self, result: list=None, max_chars: int=79):
        if result is None:
            self.result = []
        else:
            self.result = result
        self.max_chars = max_chars

    def format_steam_info(self, app: SteamApp) -> str:
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

        self.result.append(f'*** {app.title} ({rel_date}) ***')
        self.result.append(f'{current}{currency} ({app.discount}% '
                           f'from {initial}{currency})')
        self.result.append(f'Metacritic score: {app.metacritic}')

        return self._center_text(self.result)

    def format_steam_website_info(self, app: SteamApp) -> str:
        """
        Formats information that was gathered from Steam website.

        :param app: steam application from which info has to be formatted.
        :return: formatted string.
        """

        self.result.append('-')

        if app.overall_count:
            self.result.append(f'{app.overall_count} overall reviews '
                               f'({app.overall_percent} positive)')
        else:
            self.result.append("No overall reviews available")

        # It makes sense to show absence of recent reviews only if overall
        # reviews are missing as well.
        if app.overall_count and not app.recent_count:
            self.result.append("No recent reviews available")

        if app.recent_count:
            self.result.append(f'{app.recent_count} recent reviews '
                               f'({app.recent_percent} positive)')

        return self._center_text(self.result)

    def format_historical_low(self, app: SteamApp) -> str:
        """
        Formats information on historical low prices of the given application.

        :param app: steam application from which info has to be formatted.
        :return: formatted string.
        """

        self.result.append('-')

        lowest = f'{app.historical_low:.2f}' if app.historical_low else 'N/A'
        currency = f' {app.currency}' if app.currency else ''
        cut = app.historical_cut if app.historical_cut else 'N/A'
        shop = app.historical_shop if app.historical_shop else 'N/A'

        self.result.append(f'Historical low: {lowest}{currency} (-{cut}%). '
                           f'Shop: {shop}')

        return self._center_text(self.result)

    def format_description(self, app: SteamApp) -> str:
        """
        Formats given application's description.

        :param app: steam application from which info has to be formatted.
        :return: formatted string.
        """

        self.result.append('-')

        if app.description:
            self.result.append(app.description)
        else:
            self.result.append('Short description unavailable')

        return self._center_text(self.result)

    def print_results(self):
        print("\n" + "".center(self.max_chars, '*') + '\n')
        print(self._center_text(self.result))
        print("\n" + "".center(self.max_chars, '*') + '\n')

    def _center_text(self, text: list) -> str:
        """
        Helper method that centers given text.

        :param text: list with string values that need to be centered.
        :return: centered string.
        """

        return '\n'.join(line.center(self.max_chars) for line in text)
