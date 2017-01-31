import unittest

from unittest import mock

from steamCLI.results import Results


class ResultTest(unittest.TestCase):
    """ Test suite to make sure correct information is returned. """

    def setUp(self):
        self.results = Results()

    def test_steam_info_should_construct_centered_description(self):
        """ Ensures passing valid info constructs expected string. """

        app = mock.Mock()
        app.title = 'Borderlands'
        app.release_date = '10 10 2010'
        app.current = 1000
        app.currency = 'GBP'
        app.discount = '0'
        app.initial = 1000
        app.meta = '99'

        result = self.results.construct_steam_info(app)

        expected = list()
        expected.append(f'*** {app.title} ({app.release_date}) ***')
        expected.append(f'10.0 {app.currency} ({app.discount}% '
                        f'from 10.0 {app.currency})')
        expected.append(f'Metacritic score: {app.meta}')

        self.assertEqual('\n'.join(ln.center(79) for ln in expected), result)

    def test_steam_info_without_valid_inputs(self):
        """ Ensure that null/empty values are correctly represented. """

        app = mock.Mock()
        app.title = 'Borderlands'
        app.release_date = None
        app.meta = None
        app.current = None
        app.initial = None
        app.currency = None
        app.discount = '0'

        result = self.results.construct_steam_info(app)

        expected = list()
        expected.append('*** Borderlands (no release date) ***')
        expected.append('N/A (0% from N/A)')
        expected.append('Metacritic score: None')

        self.assertEqual(result, '\n'.join(ln.center(79) for ln in expected))

