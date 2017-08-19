# To run single test module:
# >>> python -m unittest test.test_some_module

import os
import unittest
from unittest import mock

from steamCLI.config import Config


class ConfigTests(unittest.TestCase):
    @mock.patch('steamCLI.config.os.path.isfile')
    def test_should_create_config_given_valid_path(self, mocked_isfile):
        test_path = 'valid_path.ini'
        mocked_isfile.return_value = True

        config = Config(test_path)

        self.assertTrue(config)
        self.assertIn(mock.call(test_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_should_aggregate_multiple_config_arguments_into_path(self, mocked_isfile):
        test_path = 'deepfolder/folder/config.ini'
        mocked_isfile.return_value = True
        arguments = test_path.split('/')

        config = Config(arguments[0], arguments[1], arguments[2])

        self.assertTrue(config)
        self.assertIn(mock.call(test_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_should_support_different_root(self, mocked_isfile):
        test_path = '/rooty/root/'
        mocked_isfile.return_value = True

        config = Config(root_folder=test_path)

        self.assertTrue(config)
        self.assertIn(mock.call(test_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_should_throw_no_file_exception(self, mocked_isfile):
        mocked_isfile.return_value = False
        with self.assertRaises(FileNotFoundError):
            Config('nonexistent.ini')

    def test_config_should_return_correct_real_values(self):
        """ Note: test depends on external file. Hence, it is very brittle. """

        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'steamCLI')

        config = Config(dir_path, 'resources.ini')

        self.assertEqual(
            config.get_value('SteamAPIs', 'applist'),
            'http://api.steampowered.com/ISteamApps/GetAppList/v0002/'
        )
