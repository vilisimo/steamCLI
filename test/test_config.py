import unittest
import os

from unittest import mock

from steamCLI.config import Config

# To run single test module:
# >>> python -m unittest test.test_some_module


class ConfigTests(unittest.TestCase):
    """ Test suite for config.py. """

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_config_creation(self, mocked_isfile):
        """ Ensure that the file can be created when it exists. """

        test_path = 'someplace.ini'
        mocked_isfile.return_value = True
        config = Config(test_path)

        self.assertTrue(config)
        self.assertIn(mock.call(test_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_config_creation_multiple_variables(self, mocked_isfile):
        """ Ensure path is created when multiple variables are given. """

        test_path = 'deepfolder/folder/somepath.ini'
        mocked_isfile.return_value = True
        arguments = test_path.split('/')
        config = Config(arguments[0], arguments[1], arguments[2])

        self.assertTrue(config)
        self.assertIn(mock.call(test_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_config_creation_different_root(self, mocked_isfile):
        """ 
        Ensure that a different root is supported (though it should not be 
        needed for this application).
        """

        test_path = 'rooty/root/'
        mocked_isfile.return_value = True
        config = Config(root=test_path)

        self.assertTrue(config)
        self.assertIn(mock.call(test_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_config_no_file(self, mocked_isfile):
        """ Ensure that an exception is thrown if a file does not exist. """

        mocked_isfile.return_value = False
        with self.assertRaises(FileNotFoundError):
            Config('somepath.ini')

    def test_config_returns_correct_values(self):
        """
        Ensure config file is read and values are found.

        Note: test depends on external file. Would break if the file changes.
        """

        config = Config('steamCLI', 'resources.ini')

        self.assertEqual(
            config.get_value('SteamAPIs', 'applist'),
            'http://api.steampowered.com/ISteamApps/GetAppList/v0002/'
        )
