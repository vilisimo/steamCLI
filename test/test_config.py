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

        mocked_isfile.return_value = True
        config = Config('somepath.ini')

        self.assertTrue(config)
        self.assertIn(mock.call('somepath.ini'), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_config_creation_multiple_variables(self, mocked_isfile):
        """ Ensure path is created when multiple variables are given. """

        mocked_isfile.return_value = True
        expected_path = 'deepfolder/folder/somepath.ini'
        arguments = expected_path.split('/')
        config = Config(arguments[0], arguments[1], arguments[2])

        self.assertTrue(config)
        self.assertIn(mock.call(expected_path), mocked_isfile.call_args_list)

    @mock.patch('steamCLI.config.os.path.isfile')
    def test_config_creation_different_root(self, mocked_isfile):
        """ 
        Ensure that a different root is supported (though it should not be 
        needed for this application).
        """

        root = 'some_other_root/'
        config = Config(root=root)

        self.assertTrue(config)
        self.assertIn(mock.call(root), mocked_isfile.call_args_list)

    def test_config_no_file(self):
        """ Ensure that an exception is thrown is a file does not exist. """

        with self.assertRaises(FileNotFoundError):
            Config('somepath.ini')

    def test_construct_path(self):
        """ Ensure absolute path is constructed properly """

        name = os.path.basename(__file__)
        folder = os.path.basename(os.path.dirname(__file__))
        config = Config(root='steamCLI/resources.ini')
        actual_path = config._construct_path(folder, name)
        expected_path = os.path.abspath(__file__)

        self.assertEqual(expected_path, actual_path)

    def test_config_returns_correct_values(self):
        """
        Ensure config file is read and values are found.

        Note: test depends on external file. Would break if the file changes.
        """

        config = Config('steamCLI', 'resources.ini')

        self.assertEqual(
            config.get_value('SteamAPIs', 'applist'),
            'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'
        )
