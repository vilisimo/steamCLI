import unittest

from steamCLI.results import Results
from steamCLI.steamapp import SteamApp


class ResultTest(unittest.TestCase):
    """ Test suite to make sure correct information is returned. """

    def setUp(self):
        self.app = SteamApp(config="placeholder")
        self.results = Results(app=self.app)

    def test_steam_info_should_construct_centered_description(self):
        """ Ensures passing valid info constructs expected string. """

        self.app.title = 'Borderlands'
        self.app.release_date = '10 10 2010'
        self.app.final_price = 100
        self.app.currency = 'GBP'
        self.app.discount = '0'
        self.app.initial_price = 100
        self.app.metacritic = '99'
        self.results.format_steam_info()
        expected = [f'*** {self.app.title} ({self.app.release_date}) ***',
                    f'1.0 {self.app.currency} ({self.app.discount}% from 1.0 '
                    f'{self.app.currency})',
                    f'Metacritic score: {self.app.metacritic}']

        self.assertEqual(expected, self.results.steam)

    def test_steam_info_without_valid_inputs(self):
        """ Ensure that null/empty values are correctly represented. """

        expected = ['*** Borderlands (no release date) ***',
                    'N/A (0% from N/A)',
                    'Metacritic score: None']

        self.app.title = 'Borderlands'
        self.app.release_date = None
        self.app.metacritic = None
        self.app.final_price = None
        self.app.initial_price = None
        self.app.currency = None
        self.app.discount = '0'
        self.results.format_steam_info()

        self.assertEqual(expected, self.results.steam)

    def test_app_scores_no_missing_info(self):
        """ Ensures that app scores are formatted correctly. """

        expected = ['1000 overall reviews (99% positive)',
                    '100 recent reviews (99% positive)']

        self.app.overall_count = '1000'
        self.app.overall_percent = '99%'
        self.app.recent_count = '100'
        self.app.recent_percent = '99%'
        self.results.format_steam_website_info()

        self.assertEqual(expected, self.results.website)

    def test_app_scores_missing_all_info(self):
        """ Ensures that app scores are reported missing. """

        expected = ["No overall reviews available"]
        self.results.format_steam_website_info()

        self.assertEqual(expected, self.results.website)

    def test_app_scores_recent_missing(self):
        """ Ensures that recent app scores are reported missing. """

        expected = ['1000 overall reviews (99% positive)',
                    'No recent reviews available']

        self.app.overall_count = '1000'
        self.app.overall_percent = '99%'
        self.results.format_steam_website_info()

        self.assertEqual(expected, self.results.website)

    def test_app_scores_overall_missing(self):
        """ Ensures that overall app scores are reported missing. """

        expected = ['No overall reviews available',
                    '1000 recent reviews (99% positive)']

        self.app.recent_count = '1000'
        self.app.recent_percent = '99%'
        self.results.format_steam_website_info()

        self.assertEqual(expected, self.results.website)

    def test_format_historical_low_valid_inputs(self):
        """
        Ensure that information on historical low prices is formatted
        properly.
        """

        expected = ['Historical low: 10.99 GBP (-50%)', 'Shop: Steam']

        self.app.historical_low = 10.99
        self.app.historical_cut = 50
        self.app.currency = 'GBP'
        self.app.historical_shop = 'Steam'
        self.results.format_historical_low()

        self.assertEqual(expected, self.results.itad)

    def test_format_historical_low_nonexistent_inputs(self):
        """
        Ensure that when the information is not found, user is presented
        with a user friendly(-ish) result.
        """

        expected = ['Historical low: N/A (-N/A%)', 'Shop: N/A']
        self.results.format_historical_low()

        self.assertEqual(expected, self.results.itad)

    def test_format_description_with_valid_description(self):
        """ Ensures that description is properly formatted. """

        expected = "Test Description"
        self.app.description = "Test Description"
        self.results.format_description()

        self.assertEqual(expected, self.results.description)

    def test_format_description_with_missing_description(self):
        """
        Ensures that given non-existent description, user is informed
        about it.
        """

        expected = "Short description unavailable"
        self.results.format_description()

        self.assertEqual(expected, self.results.description)
