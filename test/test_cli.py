# To run single test module:
# >>> python -m unittest test.test_some_module

import unittest

from argparse import ArgumentError
from unittest import mock

from steamCLI.cli import _create_parser


class ParserTests(unittest.TestCase):
    """ 
    Note: at the moment of writing tests (26/12/2016) parser required either 
    title or id argument. Hence, simply passing, e.g., -d to parser would cause
    it to exit early and tests to fail.
    """

    def setUp(self):
        mock_config = mock.Mock()
        # config values we will pass to parser
        self.default_region = "uk"
        regions = 'au,br,ca,cn,eu1,eu2,ru,tr,uk,us'
        app_help = "cli app description"
        title_help = "app title"
        id_help = "app id"
        desc_help = "app description"
        region_help = "region"

        mock_config.get_value.side_effect = [
            app_help, 
            self.default_region,
            regions,
            title_help,
            id_help,
            desc_help,
            region_help,
        ]

        self.parser = _create_parser(mock_config)

    def test_creates_parser(self):
        """ Ensure the function creates parser object. """

        self.assertTrue(self.parser)

    def test_default_region(self):
        """ Ensure default region is the one that is specified. """

        args = self.parser.parse_args(['-t'])
        region = args.region

        self.assertEqual(self.default_region, region)

    def test_assigns_region(self):
        """ Ensures region can be assigned. """

        region = 'au'
        args = self.parser.parse_args(['-tr', region])

        self.assertEqual(region, args.region)

    def test_assign_region_case_insensitive(self):
        """ Ensures region is case insensitive. """

        region = 'AU'
        args = self.parser.parse_args(['-tr', region])

        self.assertEqual(region.lower(), args.region)

    def test_invalid_region(self):
        """ Make sure that entering invalid region raises an error. """

        argparse_mock = mock.MagicMock()
        with mock.patch('steamCLI.cli.argparse.ArgumentParser._print_message', 
                        argparse_mock):
            with self.assertRaises((ArgumentError, SystemExit)):
                region = 'as'
                self.parser.parse_args(['-t', '-r', region])

    def test_title_flag(self):
        """ Ensures true/false is stored when -t is passed in. """

        args = self.parser.parse_args(['-t'])

        self.assertTrue(args.title)

        args = self.parser.parse_args(['-id', '1'])

        self.assertFalse(args.title)

    def test_assigns_id(self):
        """ Ensure ID can be assigned when -id flag is used. """

        app_id = 1
        args = self.parser.parse_args(['-id', str(app_id)])

        self.assertEqual(app_id, args.appid)

    def test_description_flag(self):
        """ Ensure description is set either to true or false if -d is used. """

        args = self.parser.parse_args(['-td'])

        self.assertTrue(args.description)

        args = self.parser.parse_args(['-t'])

        self.assertFalse(args.description)
