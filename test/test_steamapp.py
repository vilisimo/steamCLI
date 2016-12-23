import unittest
import json

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
        """ Ensures _get_app_dict() manages to find relevant dictionaries """

        expected = {"appid": 8, "name": "winui2"}
        result = self.app._get_app_dict(RESOURCE)

        self.assertEqual(expected, result)

    def test_get_app_dict_case_insensitive(self):
        """ Ensure that _get_app_dict() is not case sensitive. """

        self.app.title = "WInuI2"
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

    def test_assign_id_with_id(self):
        """
        Ensure that when appid is defined upon creation of an object, no further
        processing is done, i.e. no other methods inside assign_id() are called.
        """

        app = SteamApp(appid=1)
        with mock.patch.object(app, '_fetch_text') as m:
            a = app.assign_id(self.url)

        assert not m.called, "Method should not have been called: appid exists."

        with mock.patch.object(app, '_get_app_dict') as m:
            app.assign_id(self.url)

        assert not m.called, "Method should not have been called: appid exists."

    # # In case there is a need to check it sometime later. Passes as of Dec 15.
    # def test_real_deal(self):
    #     """ Ensure everything works with a proper steam api. """
    #
    #     url = 'http://api.steampowered.com/ISteamApps/GetAppList/v0002/'
    #     app = SteamApp(title="DungeonUp")
    #     expected_id = 388620
    #     app.assign_id(url)
    #     real_id = app.appid
    #
    #     self.assertEqual(expected_id, real_id)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_fetch_json_no_resource(self, mock_get):
        """ Ensures exception is raised if app is not found. """

        fake_response = mock.Mock()
        fake_response.json.return_value = {"10": {"success": False}}

        mock_get.return_value = fake_response
        with self.assertRaises(HTTPError):
            self.app.appid = 10
            self.app._fetch_json(self.url)

        self.assertIn(mock.call(self.url), mock_get.call_args_list)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_fetch_json_resource_exists(self, mock_get):
        """ Ensures correct json is returned when a resource can be accessed """

        resource = {"10": {"success": True}}
        fake_response = mock.Mock()
        fake_response.json.return_value = resource
        mock_get.return_value = fake_response
        self.app.appid = 10
        json_data = self.app._fetch_json(self.url)

        self.assertEqual(resource, json_data)
        self.assertIn(mock.call(self.url), mock_get.call_args_list)

    def test_get_name(self):
        """
        Ensures that a name can be extracted from a correctly formed dict.
        """

        app_id = 1
        name = 'test'
        data = {str(app_id): {'data': {'name': name}}}
        self.app.appid = app_id
        actual_name = self.app._get_name(data)

        self.assertEqual(name, actual_name)

    def test_get_metacritic_score(self):
        """ Ensures that metacritic score can be extracted. """

        app_id = 1
        score = 1
        data = {str(app_id): {'data': {'metacritic': {'score': score}}}}
        self.app.appid = app_id
        metacritic = self.app._get_metacritic_score(data)

        self.assertEqual(score, metacritic)

    def test_get_price_overview(self):
        """ Ensures all relevant data is extracted from price overview. """

        app_id = 1
        data = {
            str(app_id): {
                'data': {
                    'price_overview': {
                        'currency': 'EUR',
                        'discount_percent': 50,
                        'initial': 10.00,
                        'final': 5.00,
                    }
                }
            }
        }
        self.app.appid = 1
        expected = data[str(app_id)]['data']['price_overview']
        actual = self.app._get_price_overview(data)

        self.assertEqual(expected, actual)

    def test_get_description(self):
        """ Ensures that description can be extracted. """

        app_id = 1
        description = 'test'
        data = {str(app_id): {'data': {'detailed_description': description}}}
        self.app.appid = app_id
        actual_description = self.app._get_description(data)

        self.assertEqual(description, actual_description)

        # json_data = self.app._fetch_json('http://store.steampowered.com/api/appdetails?appids=10')
        # metacritic = self.app._get_metacritic_score(json_data)
        # print(metacritic)