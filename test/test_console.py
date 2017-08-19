# To run single test module:
# >>> python -m unittest test.test_some_module

import unittest
from argparse import ArgumentError
from unittest import mock

from steamCLI.console import _create_parser


class ParserTests(unittest.TestCase):
    """ 
    Note: at the moment of writing tests (26/12/2016) parser required either 
    title or id argument. Hence, simply passing, e.g., -d to parser would cause
    it to exit early and tests to fail.
    """

    def setUp(self):
        mock_config = mock.Mock()
        self.default_region = "uk"
        mock_config.get_value.side_effect = [
            "cli app description",
            self.default_region,
            'au,br,ca,cn,eu1,eu2,ru,tr,uk,us',
            "app title",
            "app id",
            "app description",
            "reviews",
            "region",
            "historical"
        ]

        self.parser = _create_parser(mock_config)

    def test_parser_created(self):
        self.assertTrue(self.parser)

    def test_default_region_set(self):
        args = self.parser.parse_args(['-t'])

        self.assertEqual(self.default_region, args.region)

    def test_should_assign_region(self):
        args = self.parser.parse_args(['-tr', 'au'])

        self.assertEqual('au', args.region)

    def test_region_should_be_case_insensitive(self):
        args = self.parser.parse_args(['-tr', 'AU'])

        self.assertEqual('au', args.region)

    def test_should_not_allow_region_not_in_the_list(self):
        with mock.patch('steamCLI.console.ArgumentParser._print_message', mock.MagicMock()):
            with self.assertRaises((ArgumentError, SystemExit)):
                self.parser.parse_args(['-t', '-r', 'as'])

    def test_should_store_title_flag(self):
        args = self.parser.parse_args(['-t'])
        self.assertTrue(args.title)

        args = self.parser.parse_args(['-id', '1'])
        self.assertFalse(args.title)

    def test_should_assign_id_with_id_flag(self):
        args = self.parser.parse_args(['-id', "1"])

        self.assertEqual(1, args.appid)

    def test_should_store_description_flag(self):
        args = self.parser.parse_args(['-td'])
        self.assertTrue(args.description)

        args = self.parser.parse_args(['-t'])
        self.assertFalse(args.description)

    def test_should_store_review_scores_flag(self):
        args = self.parser.parse_args(['-ts'])
        self.assertTrue(args.scores)

        args = self.parser.parse_args(['-t'])
        self.assertFalse(args.scores)

    def test_should_store_historical_low_flag(self):
        args = self.parser.parse_args(['-tl'])
        self.assertTrue(args.historical_low)

        args = self.parser.parse_args(['-t'])
        self.assertFalse(args.historical_low)
