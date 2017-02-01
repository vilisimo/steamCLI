import unittest

from steamCLI.results import Results
from steamCLI.steamapp import SteamApp


class ResultTest(unittest.TestCase):
    """ Test suite to make sure correct information is returned. """

    def setUp(self):
        self.results = Results()
        self.app = SteamApp(config="placeholder")

    def test_steam_info_should_construct_centered_description(self):
        """ Ensures passing valid info constructs expected string. """

        self.app.title = 'Borderlands'
        self.app.release_date = '10 10 2010'
        self.app.final_price = 1000
        self.app.currency = 'GBP'
        self.app.discount = '0'
        self.app.initial_price = 1000
        self.app.metacritic = '99'

        result = self.results.format_steam_info(self.app)

        expected = list()
        expected.append(f'*** {self.app.title} ({self.app.release_date}) ***')
        expected.append(f'10.0 {self.app.currency} ({self.app.discount}% '
                        f'from 10.0 {self.app.currency})')
        expected.append(f'Metacritic score: {self.app.metacritic}')

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)

    def test_steam_info_without_valid_inputs(self):
        """ Ensure that null/empty values are correctly represented. """

        self.app.title = 'Borderlands'
        self.app.release_date = None
        self.app.metacritic = None
        self.app.final_price = None
        self.app.initial_price = None
        self.app.currency = None
        self.app.discount = '0'

        result = self.results.format_steam_info(self.app)

        expected = list()
        expected.append('*** Borderlands (no release date) ***')
        expected.append('N/A (0% from N/A)')
        expected.append('Metacritic score: None')

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)

    def test_app_scores_no_missing_info(self):
        """ Ensures that app scores are formatted correctly. """

        self.app.overall_count = '1000'
        self.app.overall_percent = '99%'
        self.app.recent_count = '100'
        self.app.recent_percent = '99%'
        expected = list()
        expected.append('\n')
        expected.append('1000 overall reviews (99% positive)')
        expected.append('100 recent reviews (99% positive)')
        result = self.results.format_steam_website_info(self.app)

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)

    def test_app_scores_missing_all_info(self):
        """ Ensures that app scores are reported missing. """

        expected = list()
        expected.append('\n')
        expected.append("No overall reviews available")
        result = self.results.format_steam_website_info(self.app)

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)

    def test_app_scores_recent_missing(self):
        """ Ensures that recent app scores are reported missing. """

        self.app.overall_count = '1000'
        self.app.overall_percent = '99%'
        expected = list()
        expected.append('\n')
        expected.append('1000 overall reviews (99% positive)')
        expected.append('No recent reviews available')
        result = self.results.format_steam_website_info(self.app)

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)

    def test_app_scores_overall_missing(self):
        """ Ensures that overall app scores are reported missing. """

        self.app.recent_count = '1000'
        self.app.recent_percent = '99%'
        expected = list()
        expected.append('\n')
        expected.append('No overall reviews available')
        expected.append('1000 recent reviews (99% positive)')
        result = self.results.format_steam_website_info(self.app)

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)

    def test_format_historical_low_valid_inputs(self):
        """
        Ensure that information on historical low prices is formatted
        properly.
        """

        self.app.historical_low = 10.99
        self.app.historical_cut = 50
        self.app.currency = 'GBP'
        self.app.historical_shop = 'Steam'
        expected = list()
        expected.append('\n')
        expected.append("Historical low: 10.99 GBP (-50%). Shop: Steam")
        result = self.results.format_historical_low(self.app)

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)

    def test_format_historical_low_nonexistent_inputs(self):
        """
        Ensure that when the information is not found, user is presented
        with a user friendly(-ish) result.
        """

        expected = list()
        expected.append('\n')
        expected.append("Historical low: N/A (-N/A%). Shop: N/A")
        result = self.results.format_historical_low(self.app)

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)
    # if args.historical_low:
    #     print()
    #     low = app.historical_low
    #     cut = app.historical_cut
    #     shop = app.historical_shop
    #     h_low = f"Historical low: {low:.2f} {currency} (-{cut}%). Shop: {shop}"
    #     print(h_low.center(max_chars))


    def test_format_description_with_valid_description(self):
        """ Ensures that description is properly formatted. """

        self.app.description = "Test Description"
        expected = list()
        expected.append('\n')
        expected.append("Test Description")
        result = self.results.format_description(self.app)

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)

    def test_format_description_with_missing_description(self):
        """
        Ensures that given non-existent description, user is informed
        about it.
        """

        expected = list()
        expected.append('\n')
        expected.append("Short description unavailable")
        result = self.results.format_description(self.app)

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)
