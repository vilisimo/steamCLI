# To run single test module:
# >>> python -m unittest test.test_some_module

import unittest

from unittest import mock
from requests import HTTPError

from steamCLI.steamapp import SteamApp

# Stubs that tests can use.
RESOURCE = '{"applist": {"apps": {"app": [{"appid": 8,"name": "winui2"}]}}}'
MOCK_DICT = {"appid": 8, "name": "winui2"}


class SteamAppFetchTextAssignIDTests(unittest.TestCase):
    """ Tests related to functionality necessary to find app id. """

    def setUp(self):
        self.url = 'http://api.example.com/test/'
        self.title = MOCK_DICT["name"]
        self.appid = MOCK_DICT["appid"]
        self.app = SteamApp()

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

        result = self.app._get_app_dict(RESOURCE, title=self.title)

        self.assertEqual(MOCK_DICT, result)

    def test_get_app_dict_case_insensitive(self):
        """ Ensure that _get_app_dict() is not case sensitive. """

        result = self.app._get_app_dict(RESOURCE, title=self.title.upper())

        self.assertEqual(MOCK_DICT, result)

    def test_get_app_dict_with_id(self):
        """
        Ensure that _get_app_dict() works not only with title, but with app
        id as well.
        """

        result = self.app._get_app_dict(RESOURCE, appid=self.appid)

        self.assertEqual(MOCK_DICT, result)

    def test_get_app_dict_with_id_no_such_id(self):
        """ Ensure that when the ID is wrong, nothing is found. """

        result = self.app._get_app_dict(RESOURCE, appid=0)

        self.assertFalse(result)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_text')
    @mock.patch.object(SteamApp, '_get_app_dict')
    def test_find_app_with_title(self, mock_get_dict, mock_fetch):
        """
        Ensures that an app can be found when a valid resource and a valid app
        title is provided.
        """

        mock_fetch.return_value = RESOURCE
        mock_get_dict.return_value = MOCK_DICT
        self.app.find_app(self.url, title=self.title)

        self.assertEqual(self.app.appid, MOCK_DICT['appid'])

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_text')
    @mock.patch.object(SteamApp, '_get_app_dict')
    def test_find_app_with_id(self, mock_get_dict, mock_fetch):
        """
        Ensures that an app can be found when a valid resource and a valid
        app id is provided.
        """

        mock_fetch.return_value = RESOURCE
        mock_get_dict.return_value = MOCK_DICT
        self.app.find_app(self.url, appid=self.appid)

        self.assertEqual(self.app.title, MOCK_DICT['name'])

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_text')
    @mock.patch.object(SteamApp, '_get_app_dict')
    def test_find_app_no_dict_returned(self, mock_dict, mock_fetch):
        """ Ensures that ID is not found with an invalid resource. """

        mock_fetch.return_value = RESOURCE
        mock_dict.return_value = None
        self.app.find_app(self.url)

        self.assertFalse(self.app.appid)
        self.assertFalse(self.app.title)

    # # In case there is a need to check it sometime later. Passes as of Dec 26.
    # def test_real_deal(self):
    #     """ Ensure everything works with a proper steam api. """
    #
    #     url = 'http://api.steampowered.com/ISteamApps/GetAppList/v0002/'
    #     title = "DungeonUp"
    #     app = SteamApp()
    #     expected_id = 388620
    #     app.find_app(url, title=title)
    #     real_id = app.appid
    #
    #     self.assertEqual(expected_id, real_id)

    @mock.patch('steamCLI.steamapp.requests.get')
    @mock.patch('steamCLI.config.Config.get_value')
    def test_choose_complete_json(self, mock_config, mock_get):
        """
        Ensures that _choose_one() method returns a JSON info that has
        success set as true. If no such dictionary exists, then it
        should return None.
        """

        mock_config.side_effect = ["doesn't matter", "doesn't matter"]
        # Dictionaries that we get from a list of all apps
        # (http://api.steampowered.com/ISteamApps/GetAppList/v0002/)
        applist_d1 = {"appid": 1, "name": "test"}
        applist_d2 = {"appid": 2, "name": "test"}
        applist_d3 = {"appid": 3, "name": "test"}
        dict_list = [applist_d1, applist_d2, applist_d3]
        # Stub dictionary similar to what we get accessing individual apps
        # E.g.: http://store.steampowered.com/api/appdetails?appids=10
        app_d1 = {"1": {"success": False}}
        app_d2 = {"2": {"success": False}}
        app_d3 = {"3": {"success": True}}
        fake_r1 = mock.Mock()
        fake_r2 = mock.Mock()
        fake_r3 = mock.Mock()
        fake_r1.json.return_value = app_d1
        fake_r2.json.return_value = app_d2
        fake_r3.json.return_value = app_d3
        mock_get.side_effect = [fake_r1, fake_r2, fake_r3]
        json_data = self.app._choose_complete_json(dict_list)

        fake_r1.json.assert_called_with()
        fake_r2.json.assert_called_with()
        fake_r3.json.assert_called_with()
        mock_config.assert_called()
        self.assertEqual(applist_d3, json_data)

    @mock.patch('steamCLI.steamapp.requests.get')
    @mock.patch('steamCLI.config.Config.get_value')
    def test_choose_complete_json_no_success(self, mock_config, mock_get):
        """
        Ensures that when dicts passed do not have success: True None is
        returned.
        """

        mock_config.side_effect = ["doesn't matter", "doesn't matter"]
        applist_dict = {"appid": 1, "name": "test"}
        dict_list = [applist_dict, ]
        app_dict = {"1": {"success": False}}
        fake_response = mock.Mock()
        fake_response.json.return_value = app_dict
        mock_get.return_value = fake_response
        json_data = self.app._choose_complete_json(dict_list)

        fake_response.json.assert_called_with()
        mock_config.assert_called()
        self.assertFalse(json_data)

    def test_choose_complete_json_passed_empty_list(self):
        """ Ensure empty list does not break the function. """

        empty_list = []
        json_data = self.app._choose_complete_json(empty_list)

        self.assertFalse(json_data)


class SteamAppAssignInfoTests(unittest.TestCase):
    """
    Tests related to functionality necessary for assignment of values to
    various fields, such as title, price, metacritic info, etc.
    """

    def setUp(self):
        self.id = 1
        self.url = 'http://api.example.com/test/'
        self.app = SteamApp()
        self.app.appid = self.id

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

    @mock.patch('steamCLI.config.Config.get_value')
    def test_get_steam_app_url(self, mock_config):
        """ Ensure a correct url is constructed depending on region. """

        mock_config.return_value = 'nevermind'
        region = "au"
        url = self.app._get_steam_app_url(region)

        mock_config.assert_called()
        self.assertTrue(url.endswith(region))

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
        metacritic = self.app._get_metascore(self.response)

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
    def test_assign_steam_info_title(self, mock_fetch):
        """ Ensures assign_json_info() assigns title. """

        mock_fetch.return_value = self.response
        self.app.assign_steam_info()
        expected_title = self.response[str(self.id)]['data']['name']

        self.assertEqual(expected_title, self.app.title)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_steam_info_release_date(self, mock_fetch):
        """ Ensures assign_json_info() assigns a release date. """

        mock_fetch.return_value = self.response
        self.app.assign_steam_info()
        expected_date = self.response[str(self.id)]['data']['release_date'][
            'date']

        self.assertEqual(expected_date, self.app.release_date)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_steam_info_metacritic(self, mock_fetch):
        """ Ensures assign_info() assigns metacritic score. """

        mock_fetch.return_value = self.response
        self.app.assign_steam_info()
        score = self.response[str(self.id)]['data']['metacritic']['score']

        self.assertEqual(score, self.app.metascore)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_steam_info_description(self, mock_fetch):
        """ Ensures assign_info() assigns description. """

        mock_fetch.return_value = self.response
        self.app.assign_steam_info()
        desc = self.response[str(self.id)]['data']['short_description']

        self.assertEqual(desc, self.app.description)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_steam_info_initial_price(self, mock_fetch):
        """ Ensures assign_info() assigns initial price. """

        mock_fetch.return_value = self.response
        self.app.assign_steam_info()
        price = self.response[str(self.id)]['data']['price_overview']['initial']

        self.assertEqual(price, self.app.initial_price)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_steam_info_final_price(self, mock_fetch):
        """ Ensures assign_info() assigns final price. """

        mock_fetch.return_value = self.response
        self.app.assign_steam_info()
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
    def test_assign_steam_info_currency(self, mock_fetch):
        """ Ensures assign_info() assigns currency. """

        mock_fetch.return_value = self.response
        self.app.assign_steam_info()
        cur = self.response[str(self.id)]['data']['price_overview']['currency']

        self.assertEqual(cur, self.app.currency)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    def test_assign_steam_info_currency_no_price_overview(self, mock_fetch):
        """
        Ensure that when the price is not available, price_overview dict is
        not given any values, and hence anything else is not given values, too.
        """

        self.response[str(self.id)]['data']['price_overview'] = None
        mock_fetch.return_value = self.response
        self.app.assign_steam_info()

        self.assertFalse(self.app.currency)
        self.assertFalse(self.app.initial_price)
        self.assertFalse(self.app.final_price)
        self.assertFalse(self.app.discount)

    @mock.patch('steamCLI.steamapp.SteamApp._fetch_json')
    @mock.patch('steamCLI.steamapp.SteamApp._get_steam_app_url')
    def test_assign_steam_info(self, mock_get_url, mock_fetch):
        """ Tests whether the function works given correct data. """

        mock_get_url.return_value = 'does not matter'
        mock_fetch.return_value = self.response
        self.app.assign_steam_info()

        self.assertTrue(self.app.release_date)
        self.assertTrue(self.app.description)
        self.assertTrue(self.app.metascore)
        self.assertTrue(self.app.currency)
        self.assertTrue(self.app.initial_price)
        self.assertTrue(self.app.final_price)
        self.assertTrue(self.app.discount)


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
