import unittest

from unittest import mock
from requests import HTTPError

from steamCLI.steamapp import SteamApp

# To run single test module:
# >>> python -m unittest test.test_some_module

# Fake resource that calls access
RESOURCE = '{"applist": {"apps": {"app": [{"appid": 8,"name": "winui2"}]}}}'


class SteamAppTests(unittest.TestCase):

    def setUp(self):
        self.url = 'http://api.example.com/test/'
        self.title = "winui2"
        self.app = SteamApp(self.title)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_fetch_text(self, mock_get):
        """ Ensures an error is thrown if resource cannot be accessed. """

        mock_get.side_effect = HTTPError()

        with self.assertRaises(HTTPError):
            self.app._fetch_text(self.url)
        self.assertIn(mock.call(self.url), mock_get.call_args_list)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_fetch_text_exists(self, mock_get):
        """ Ensures a textual repr. is returned if resource can be accessed. """

        mock_get.return_value = mock.MagicMock(text=RESOURCE)
        actual = self.app._fetch_text(self.url)

        self.assertEqual(RESOURCE, actual)
        self.assertIn(mock.call(self.url), mock_get.call_args_list)

    def test_get_app_dict_no_such_app(self):
        """ Ensures that when nothing is found, None is returned. """

        self.app.title = "Test"
        result = self.app._get_app_dict(RESOURCE)

        self.assertFalse(result)

    def test_get_app_dict(self):
        """ Ensures get_app_dict() manages to find relevant dictionaries """

        expected = {"appid": 8, "name": "winui2"}
        result = self.app._get_app_dict(RESOURCE)

        self.assertEqual(expected, result)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_text')
    def test_assign_id(self, mock_fetch):
        """ Ensures that ID can be found when a valid resource is provided. """

        mock_fetch.return_value = RESOURCE
        self.app.assign_id(self.url)

        self.assertEqual(self.app.appid, 8)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_text')
    @mock.patch.object(SteamApp, '_get_app_dict')
    def test_assign_id_no_dict_returned(self, mock_dict, mock_fetch):
        """ Ensures that ID is not found with an invalid resource. """

        mock_fetch.return_value = RESOURCE
        mock_dict.return_value = None
        self.app.assign_id(self.url)

        self.assertFalse(self.app.appid)

    # # In case there is a need to check it sometime later. Passes as of Dec 15.
    # def test_real_deal(self):
    #     """ Ensure everything works with a proper steam api. """
    #
    #     url = 'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'
    #     app = SteamApp(title="DungeonUp")
    #     expected_id = 388620
    #     app.assign_id(url)
    #     real_id = app.appid
    #
    #     self.assertEqual(expected_id, real_id)
