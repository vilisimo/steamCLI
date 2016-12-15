import unittest

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

    def test_config_no_file(self):
        """ Ensure that an exception is thrown is a file does not exist. """

        with self.assertRaises(FileNotFoundError):
            Config('somepath.ini')

    def test_config_returns_correct_values(self):
        """
        Ensure config file is read and values are found.

        Note: test depends on external file. Would break if the file changes.
        """

        config = Config('steamCLI/resources.ini')

        self.assertEqual(
            config.get_value('SteamAPIs', 'applist'),
            'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'
        )
