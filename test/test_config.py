# To run single test module:
# >>> python -m unittest test.test_some_module

import os
import unittest
from unittest import mock

from steamCLI.config import Config


class ConfigTests(unittest.TestCase):
    """ Test suite for config.py. """

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_should_create_config_given_valid_path(self, mocked_isfile):
        """ Ensure that the file can be created when it exists. """

        test_path = 'someplace.ini'
        mocked_isfile.return_value = True
        config = Config(test_path)

        self.assertTrue(config)
        self.assertIn(mock.call(test_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_should_ceate_config_given_multiple_variables(self, mocked_isfile):
        """ Ensure path is created when multiple variables are given. """

        test_path = 'deepfolder/folder/somepath.ini'
        mocked_isfile.return_value = True
        arguments = test_path.split('/')
        config = Config(arguments[0], arguments[1], arguments[2])

        self.assertTrue(config)
        self.assertIn(mock.call(test_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_should_support_different_root(self, mocked_isfile):
        """ 
        Ensure that a different root is supported (though it should not be 
        needed for this application).
        """

        test_path = '/rooty/root/'
        mocked_isfile.return_value = True
        config = Config(root_folder=test_path)

        self.assertTrue(config)
        self.assertIn(mock.call(test_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_should_throw_no_file_exception(self, mocked_isfile):
        """ Ensure that an exception is thrown if a file does not exist. """

        mocked_isfile.return_value = False
        with self.assertRaises(FileNotFoundError):
            Config('somepath.ini')

    def test_config_should_return_correct_real_values(self):
        """
        Ensure config file is read and values are found.

        Note: test depends on external file. Would break if the file changes.
        """

        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'steamCLI')
        config = Config(dir_path, 'resources.ini')

        self.assertEqual(
            config.get_value('SteamAPIs', 'applist'),
            'http://api.steampowered.com/ISteamApps/GetAppList/v0002/'
        )
