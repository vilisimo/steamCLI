import unittest
import json

from unittest import mock
from requests import HTTPError

from steamCLI.steamapp import SteamApp

# To run single test module:
# >>> python -m unittest test.test_some_module

# Fake resource that calls access
RESOURCE = '{"applist": {"apps": {"app": [{"appid": 8,"name": "winui2"}]}}}'


class SteamAppFetchTextAssignIDTests(unittest.TestCase):
    """
    Tests related to functionality necessary to find app id.
    """

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


class SteamAppAssignInfoTests(unittest.TestCase):
    """
    Tests related to functionality necessary for assignment of values to
    various fields, such as title, price, metacritic info, etc.
    """

    def setUp(self):
        self.id = 1
        self.url = 'http://api.example.com/test/'
        self.app = SteamApp(appid=self.id)

        self.response = {str(self.id): {'success': True, 'data': {
            'name': 'Test',
            'release_date': {'coming_soon': False, 'date': '1 Nov, 2000'},
            'metacritic': {'score': 1},
            'short_description': 'Test description',
            'price_overview': {
                'currency': 'GBP',
                'discount_percent': 50,
                'initial': 10.00,
                'final': 5.00
            }
        }}}

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_fetch_json_no_resource(self, mock_get):
        """ Ensures exception is raised if app is not found. """

        fake_response = mock.Mock()
        fake_response.json.return_value = {str(self.id): {"success": False}}

        mock_get.return_value = fake_response
        with self.assertRaises(HTTPError):
            self.app._fetch_json(self.url)

        self.assertIn(mock.call(self.url), mock_get.call_args_list)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_fetch_json_resource_exists(self, mock_get):
        """ Ensures correct json is returned when a resource can be accessed """

        fake_response = mock.Mock()
        fake_response.json.return_value = self.response
        mock_get.return_value = fake_response
        json_data = self.app._fetch_json(self.url)

        self.assertEqual(self.response, json_data)
        self.assertIn(mock.call(self.url), mock_get.call_args_list)

    def test_get_name(self):
        """
        Ensures that a name can be extracted from a correctly formed dict.
        """

        self.app.appid = self.id
        expected_name = self.response[str(self.id)]['data']['name']
        actual_name = self.app._get_title(self.response)

        self.assertEqual(expected_name, actual_name)

    def test_get_release_date(self):
        """ Ensures the release date of an app is extracted. """

        expected_date = self.response[str(self.id)]['data']['release_date'][
            'date']
        actual_date = self.app._get_release_date(self.response)

        self.assertEqual(expected_date, actual_date)

    def test_get_metacritic_score(self):
        """ Ensures that metacritic score can be extracted. """

        score = self.response[str(self.id)]['data']['metacritic']['score']
        metacritic = self.app._get_metacritic_score(self.response)

        self.assertEqual(score, metacritic)

    # Steam down, need to check this out once it recovers:
    # json_data = self.app._fetch_json('http://store.steampowered.com/api/appdetails?appids=10')
    # metacritic = self.app._get_metacritic_score(json_data)
    # print(metacritic)

    def test_get_price_overview(self):
        """ Ensures all relevant data is extracted from price overview. """

        expected = self.response[str(self.id)]['data']['price_overview']
        actual = self.app._get_price_overview(self.response)

        self.assertEqual(expected, actual)

    def test_get_description(self):
        """ Ensures that description can be extracted. """

        descr = self.response[str(self.id)]['data']['short_description']
        actual_description = self.app._get_description(self.response)

        self.assertEqual(descr, actual_description)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_json_info_title(self, mock_fetch):
        """ Ensures assign_json_info() assigns title. """

        mock_fetch.return_value = self.response
        self.app.assign_json_info()
        expected_title = self.response[str(self.id)]['data']['name']

        self.assertEqual(expected_title, self.app.title)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_json_info_release_date(self, mock_fetch):
        """ Ensures assign_json_info() assigns a release date. """

        mock_fetch.return_value = self.response
        self.app.assign_json_info()
        expected_date = self.response[str(self.id)]['data']['release_date'][
            'date']

        self.assertEqual(expected_date, self.app.release_date)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_json_info_metacritic(self, mock_fetch):
        """ Ensures assign_info() assigns metacritic score. """

        mock_fetch.return_value = self.response
        self.app.assign_json_info()
        score = self.response[str(self.id)]['data']['metacritic']['score']

        self.assertEqual(score, self.app.metacritic)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_json_info_description(self, mock_fetch):
        """ Ensures assign_info() assigns description. """

        mock_fetch.return_value = self.response
        self.app.assign_json_info()
        desc = self.response[str(self.id)]['data']['short_description']

        self.assertEqual(desc, self.app.description)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_json_info_initial_price(self, mock_fetch):
        """ Ensures assign_info() assigns initial price. """

        mock_fetch.return_value = self.response
        self.app.assign_json_info()
        price = self.response[str(self.id)]['data']['price_overview']['initial']

        self.assertEqual(price, self.app.initial_price)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_json_info_final_price(self, mock_fetch):
        """ Ensures assign_info() assigns final price. """

        mock_fetch.return_value = self.response
        self.app.assign_json_info()
        price = self.response[str(self.id)]['data']['price_overview']['final']

        self.assertEqual(price, self.app.final_price)

    # # Not needed at the moment - discount is calculated by taking prices.
    # @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    # def test_assign_json_info_discount(self, mock_fetch):
    #     """ Ensures assign_info() assigns price discount. """

    #     mock_fetch.return_value = self.response
    #     self.app.assign_json_info()
    #     discount = self.response[str(self.id)]['data']['price_overview'][
    #         'discount_percent']

    #     self.assertEqual(discount, self.app.discount)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_json_info_currency(self, mock_fetch):
        """ Ensures assign_info() assigns currency. """

        mock_fetch.return_value = self.response
        self.app.assign_json_info()
        cur = self.response[str(self.id)]['data']['price_overview']['currency']

        self.assertEqual(cur, self.app.currency)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_json_info_currency_no_price_overview(self, mock_fetch):
        """
        Ensure that when the price is not available, price_overview dict is
        not given any values, and hence anything else is not given values, too.
        """

        self.response[str(self.id)]['data']['price_overview'] = None
        mock_fetch.return_value = self.response
        self.app.assign_json_info()

        self.assertFalse(self.app.currency)
        self.assertFalse(self.app.initial_price)
        self.assertFalse(self.app.final_price)
        self.assertFalse(self.app.discount)


class HelperFunctionsTests(unittest.TestCase):
    """ Test suite for functions that support SteamApp's functionality. """

    def setUp(self):
        self.app = SteamApp()

    def test_calculate_discount_proper_values(self):
        """
        Ensures the function calculates correct percentage with valid values.
        """

        initial = 100.00
        current = 50.00
        expected = -50
        percent = self.app._calculate_discount(initial, current)

        self.assertEqual(expected, percent)

    def test_calculate_discount_doubles(self):
        """ Ensures correct percentages are derived from doubles. """

        initial = 29.99
        current = 7.49
        expected = -75
        percent = self.app._calculate_discount(initial, current)

        self.assertEqual(expected, percent)

    def test_calculate_price_higher_than_before(self):
        """ Ensure that initial < current does not break the function """

        initial = 1
        current = 3
        expected = 200
        percent = self.app._calculate_discount(initial, current)

        self.assertEqual(expected, percent)

    def test_calculate_price_zero(self):
        """ Ensure that zero initial/current does not break the function. """

        initial = 0
        current = 3
        expected = 300
        percent = self.app._calculate_discount(initial, current)

        self.assertEqual(expected, percent)

    def test_calculate_app_free(self):
        """ Ensure that when a game/app is free, discount is shown as -100%. """

        initial = 16456.46
        current = 0
        expected = -100
        percent = self.app._calculate_discount(initial, current)

        self.assertEqual(expected, percent)
