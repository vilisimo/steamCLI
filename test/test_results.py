import unittest

from steamCLI.results import Results
from steamCLI.steamapp import SteamApp


class ResultTest(unittest.TestCase):
    def setUp(self):
        self.app = SteamApp(config="placeholder")
        self.results = Results(app=self.app)

    def test_steam_info_should_construct_description(self):
        self.app.title = 'Borderlands'
        self.app.release_date = '10 10 2010'
        self.app.final_price = 100
        self.app.currency = 'GBP'
        self.app.discount = '0'
        self.app.initial_price = 100
        self.app.metacritic = '99'
        expected = [f'*** {self.app.title} ({self.app.release_date}) ***',
                    f'1.0 {self.app.currency} ({self.app.discount}% from 1.0 '
                    f'{self.app.currency})',
                    f'Metacritic score: {self.app.metacritic}']

        self.results.format_steam_info()

        self.assertEqual(expected, self.results.steam)

    def test_steam_info_without_valid_inputs_still_formatted(self):
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

    def test_app_scores_no_missing_info_formatted(self):
        expected = ['1000 overall reviews (99% positive)', '100 recent reviews (99% positive)']
        self.app.overall_count = '1000'
        self.app.overall_percent = '99%'
        self.app.recent_count = '100'
        self.app.recent_percent = '99%'

        self.results.format_steam_website_info()

        self.assertEqual(expected, self.results.site_stats)

    def test_app_scores_missing_all_info(self):
        expected = ["No overall reviews available"]

        self.results.format_steam_website_info()

        self.assertEqual(expected, self.results.site_stats)

    def test_recent_app_scores_reported_missing(self):
        self.app.overall_count = '1000'
        self.app.overall_percent = '99%'
        expected = ['1000 overall reviews (99% positive)', 'No recent reviews available']

        self.results.format_steam_website_info()

        self.assertEqual(expected, self.results.site_stats)

    def test_overall_app_scores_reported_missing(self):
        self.app.recent_count = '1000'
        self.app.recent_percent = '99%'
        expected = ['No overall reviews available', '1000 recent reviews (99% positive)']

        self.results.format_steam_website_info()

        self.assertEqual(expected, self.results.site_stats)

    def test_historical_low_with_valid_inputs_formatting(self):
        self.app.historical_low = 10.99
        self.app.historical_cut = 50
        self.app.currency = 'GBP'
        self.app.historical_shop = 'Steam'
        expected = ['Historical low: 10.99 GBP (-50%)', 'Shop: Steam']

        self.results.format_historical_low()

        self.assertEqual(expected, self.results.itad)

    def test_historical_low_with_nonexistent_inputs_formatting(self):
        expected = ['Historical low: N/A (-N/A%)', 'Shop: N/A']

        self.results.format_historical_low()

        self.assertEqual(expected, self.results.itad)

    def test_description_with_valid_description_formatting(self):
        expected = "Test Description"
        self.app.description = "Test Description"

        self.results.format_description()

        self.assertEqual(expected, self.results.description)

    def test_description_with_missing_description_formatting(self):
        expected = "Short description unavailable"

        self.results.format_description()

        self.assertEqual(expected, self.results.description)
