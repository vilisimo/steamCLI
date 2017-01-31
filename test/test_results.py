import unittest

from unittest import mock

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

        self.assertEqual(result, '\n'.join(ln.center(79) for ln in expected))

    def test_app_scores_no_missing_info(self):
        """ Ensure that app scores are formatted correctly. """

        self.app.overall_count = '1000'
        self.app.overall_percent = '99%'
        self.app.recent_count = '100'
        self.app.recent_percent = '99%'
        expected = list()
        expected.append('\n')
        expected.append('1000 overall reviews (99% positive)')
        expected.append('100 recent reviews (99% positive)')
        result = self.results.format_steam_website_info(self.app)

        self.assertEqual(result, '\n'.join(ln.center(79) for ln in expected))

    def test_app_scores_missing_all_info(self):
        """ Ensure that app scores are reported missing. """

        expected = list()
        expected.append('\n')
        expected.append("No overall reviews available")
        result = self.results.format_steam_website_info(self.app)

        self.assertEqual(result, '\n'.join(ln.center(79) for ln in expected))

    def test_app_scores_recent_missing(self):
        """ Ensure that recent app scores are reported missing. """

        self.app.overall_count = '1000'
        self.app.overall_percent = '99%'
        expected = list()
        expected.append('\n')
        expected.append('1000 overall reviews (99% positive)')
        expected.append('No recent reviews available')
        result = self.results.format_steam_website_info(self.app)

        self.assertEqual(result, '\n'.join(ln.center(79) for ln in expected))

    def test_app_scores_overall_missing(self):
        """ Ensure that overall app scores are reported missing. """

        self.app.recent_count = '1000'
        self.app.recent_percent = '99%'
        expected = list()
        expected.append('\n')
        expected.append('No overall reviews available')
        expected.append('1000 recent reviews (99% positive)')
        result = self.results.format_steam_website_info(self.app)

        self.assertEqual(result, '\n'.join(ln.center(79) for ln in expected))

        # if args.scores:
        #     print()
        #     if not app.overall_count:
        #         print("No reviews available".center(max_chars))
        #     if app.overall_count:
        #         overall_c = app.overall_count
        #         overall_p = app.overall_percent
        #         reviews = f"{overall_c} overall reviews ({overall_p} positive)"
        #         print(reviews.center(max_chars))
        #     if app.overall_count and not app.recent_count:
        #         print("No recent reviews available".center(max_chars))
        #     if app.recent_count:
        #         recent_c = app.recent_count
        #         recent_p = app.recent_percent
        #         reviews = f"{recent_c} recent reviews ({recent_p} positive)"
        #         print(reviews.center(max_chars))

