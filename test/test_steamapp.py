# To run single test module:
# >>> python -m unittest test.test_some_module

import unittest

from unittest import mock
from requests import HTTPError

from steamCLI.steamapp import SteamApp

# Stubs that tests can use.
RESOURCE = '{"applist": {"apps": {"app": [{"appid": 8,"name": "winui2"}]}}}'
MOCK_DICT = {"appid": 8, "name": "winui2"}
MOCK_DATA = {"8": {"success": True, "data": {}}}


class SteamAppFetchTextAssignIDTests(unittest.TestCase):
    """ Tests related to functionality necessary to find app id. """

    def setUp(self):
        self.url = 'http://api.example.com/test/'
        self.title = MOCK_DICT["name"]
        self.appid = MOCK_DICT["appid"]
        self.app = SteamApp()

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_fetch_resource_error(self, mock_get):
        """ Ensures an error is thrown if resource cannot be accessed. """

        mock_get.side_effect = HTTPError()

        with self.assertRaises(HTTPError):
            self.app._fetch_resource(self.url)
        self.assertIn(mock.call(self.url), mock_get.call_args_list)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_fetch_resource_exists_json(self, mock_get):
        """ Ensures json can be requested instead of textual repr. """

        mock_obj = mock.Mock()
        mock_obj.json.return_value = MOCK_DATA
        mock_get.return_value = mock_obj
        actual = self.app._fetch_resource(self.url, text=False)

        self.assertEqual(MOCK_DATA, actual)
        mock_obj.json.assert_called_once()

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_fetch_resource_exists_text(self, mock_get):
        """ Ensures a textual repr. is returned if resource can be accessed. """

        mock_get.return_value = mock.MagicMock(text=RESOURCE)
        actual = self.app._fetch_resource(self.url)

        self.assertEqual(RESOURCE, actual)
        self.assertIn(mock.call(self.url), mock_get.call_args_list)

    @mock.patch('steamCLI.steamapp.SteamApp._choose_complete_json')
    def test_download_app_data_no_such_app(self, mock_choose):
        """ Ensures that when nothing is found, None is returned. """

        mock_choose.return_value = None
        self.app.title = "Test"
        result = self.app._download_app_data(RESOURCE)

        self.assertFalse(result)
        mock_choose.assert_called_once()

    @mock.patch('steamCLI.steamapp.SteamApp._choose_complete_json')
    def test_download_app_data(self, mock_choose):
        """
        Ensures _download_app_data() manages to find relevant dictionaries.
        """

        mock_choose.return_value = MOCK_DATA
        result = self.app._download_app_data(RESOURCE, title=self.title)

        self.assertEqual(MOCK_DATA, result)
        mock_choose.assert_called_once()
    
    @mock.patch('steamCLI.steamapp.SteamApp._choose_complete_json')
    def test_download_app_data_case_insensitive(self, mock_choose):
        """ Ensure that _download_app_data() is not case sensitive. """

        mock_choose.return_value = MOCK_DATA
        result = self.app._download_app_data(RESOURCE, title=self.title.upper())

        self.assertEqual(MOCK_DATA, result)
        mock_choose.assert_called_once()

    @mock.patch('steamCLI.steamapp.SteamApp._choose_complete_json')
    def test_download_app_data_with_id(self, mock_choose):
        """
        Ensure that _download_app_data() works not only with title, but with
        app id as well.
        """

        mock_choose.return_value = MOCK_DATA
        result = self.app._download_app_data(RESOURCE, appid=self.appid)

        self.assertEqual(MOCK_DATA, result)
        mock_choose.assert_called_once()

    @mock.patch('steamCLI.steamapp.SteamApp._choose_complete_json')
    def test_get_app_dict_with_id_no_such_id(self, mock_choose):
        """ Ensure that when the ID is wrong, nothing is found. """

        mock_choose.return_value = None
        result = self.app._download_app_data(RESOURCE, appid=0)

        self.assertFalse(result)
        mock_choose.assert_called_once()

    @mock.patch.object(SteamApp, '_fetch_resource')
    @mock.patch.object(SteamApp, '_download_app_data')
    @mock.patch.object(SteamApp, '_assign_steam_info')
    def test_find_app_with_title(self, mock_assign, mock_get_data, mock_fetch):
        """
        Ensures that an app can be found when a valid resource and a valid app
        title is provided.
        """

        mock_fetch.return_value = RESOURCE
        mock_get_data.return_value = MOCK_DATA
        self.app.find_app(self.url, title=self.title)

        mock_assign.assert_called_with(MOCK_DATA)
        mock_get_data.assert_called_with(RESOURCE, appid=None,
                                         region=None, title=self.title)

    @mock.patch.object(SteamApp, '_fetch_resource')
    @mock.patch.object(SteamApp, '_download_app_data')
    @mock.patch.object(SteamApp, '_assign_steam_info')
    def test_find_app_with_id(self, mock_assign, mock_get_data, mock_fetch):
        """
        Ensures that an app can be found when a valid resource and a valid
        app id is provided.
        """

        mock_fetch.return_value = RESOURCE
        mock_get_data.return_value = MOCK_DATA
        self.app.find_app(self.url, appid=self.appid)

        mock_assign.assert_called_with(MOCK_DATA)
        mock_get_data.assert_called_with(RESOURCE, appid=self.appid,
                                         region=None, title=None)

    @mock.patch.object(SteamApp, '_fetch_resource')
    @mock.patch.object(SteamApp, '_download_app_data')
    @mock.patch.object(SteamApp, '_assign_steam_info')
    def test_find_app_no_data(self, mock_assign, mock_get_data, mock_fetch):
        """ Ensures that ID is not found with an invalid resource. """

        mock_fetch.return_value = RESOURCE
        mock_get_data.return_value = None
        self.app.find_app(self.url)

        mock_assign.assert_called_with(None)
        mock_get_data.assert_called_with(RESOURCE, appid=None, region=None,
                                         title=None)

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
        app_d3 = {"3": {"success": True, "data": {"test": {}}}}
        fake_r1 = mock.Mock()
        fake_r2 = mock.Mock()
        fake_r3 = mock.Mock()
        fake_r1.json.return_value = app_d1
        fake_r2.json.return_value = app_d2
        fake_r3.json.return_value = app_d3
        mock_get.side_effect = [fake_r1, fake_r2, fake_r3]
        json_data = self.app._choose_complete_json(dict_list)

        fake_r1.json.assert_called_once()
        fake_r2.json.assert_called_once()
        fake_r3.json.assert_called_once()
        mock_config.assert_called()
        # _choose_complete_json() returns only relevant data, hence keys.
        self.assertEqual(app_d3["3"]["data"], json_data)

    @mock.patch('steamCLI.steamapp.requests.get')
    @mock.patch('steamCLI.config.Config.get_value')
    def test_choose_complete_json_several_true(self, mock_config, mock_get):
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
        app_d2 = {"2": {"success": True, "data": {"test": {}}}}  # Stop here
        app_d3 = {"3": {"success": True, "data": {"test": {}}}}
        fake_r1 = mock.Mock()
        fake_r2 = mock.Mock()
        fake_r3 = mock.Mock()
        fake_r1.json.return_value = app_d1
        fake_r2.json.return_value = app_d2
        fake_r3.json.return_value = app_d3
        mock_get.side_effect = [fake_r1, fake_r2, fake_r3]
        json_data = self.app._choose_complete_json(dict_list)

        fake_r1.json.assert_called_once()
        fake_r2.json.assert_called_once()
        fake_r3.json.assert_not_called()  # Does not reach this one
        mock_config.assert_called()
        self.assertEqual(app_d2["2"]["data"], json_data)

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

        fake_response.json.assert_called_once()
        mock_config.assert_called()
        self.assertFalse(json_data)

    def test_choose_complete_json_passed_empty_list(self):
        """ Ensure empty list does not break the function. """

        empty_list = []
        json_data = self.app._choose_complete_json(empty_list)

        self.assertFalse(json_data)

    # # In case there is a need to check it sometime later. Passes as of Dec 26.
    # def test_real_deal(self):
    #     """ Ensure everything works with a proper steam api. """
    #
    #     url = 'http://api.steampowered.com/ISteamApps/GetAppList/v0002/'
    #     title = "DungeonUp"
    #     app = SteamApp()
    #     expected_id = 388620
    #     app.find_app(url, title=title, region='uk')
    #
    #     self.assertEqual(expected_id, app.appid)


class SteamAppAssignInfoTests(unittest.TestCase):
    """
    Tests related to functionality necessary for assignment of values to
    various fields, such as title, price, metacritic score info, etc.
    """

    def setUp(self):
        self.id = 1
        self.url = 'http://api.example.com/test/'
        self.app = SteamApp()
        self.app.appid = self.id

        self.response = {
            'name': 'Test',
            'steam_appid': 1,
            'release_date': {'coming_soon': False, 'date': '1 Nov, 2000'},
            'metacritic': {'score': 1},
            'short_description': 'Test description',
            'price_overview': {
                'currency': 'GBP',
                'discount_percent': 50,
                'initial': 10.00,
                'final': 5.00
            }
        }

    def test_get_value(self):
        """
        Ensures that _get_value() returns appropriate values given correct key.
        """

        key = 'steam_appid'
        value = self.app._get_value(self.response, key)

        self.assertEqual(self.response[key], value)

    def test_get_value_returns_none_with_incorrect_key(self):
        """
        Ensures that even when incorrect/non-existent key is supplied,
        none is returned.

        Explanation: Steam's JSON is inconsistent and some games do not
        necessarily have some of the usual information.
        """

        key = 'detailed_description'
        value = self.app._get_value(self.response, key)

        self.assertFalse(value)

    def test_get_nested_value(self):
        """
        Ensures that _get_nested_value() returns appropriate values given
        correct keys.
        """

        outer_key = 'price_overview'
        inner_key = 'currency'
        value = self.app._get_nested_value(self.response, outer_key, inner_key)

        self.assertEqual(self.response[outer_key][inner_key], value)

    def test_get_nested_value_outer_nonexistent_returns_none(self):
        """
        Ensures that when the outer key is not found, value return is
        equal to None.

        Explanation: Steam's JSON is inconsistent and some games do not
        necessarily have some of the usual information.
        """

        outer_key = 'price'
        inner_key = 'currency'

        value = self.app._get_nested_value(self.response, outer_key, inner_key)

        self.assertFalse(value)

    def test_get_nested_value_inner_nonexistent_returns_none(self):
        """
        Ensures that when the inner key is not found, value returned is
        equal to None.

        Explanation: Steam's JSON is inconsistent and some games do not
        necessarily have some of the usual information.
        """

        outer_key = 'price_overview'
        inner_key = 'price'

        value = self.app._get_nested_value(self.response, outer_key, inner_key)

        self.assertFalse(value)

    def test_assign_steam_info(self):
        """ Tests whether the function works given correct data. """

        self.app._assign_steam_info(self.response)

        self.assertTrue(self.app.release_date)
        self.assertTrue(self.app.description)
        self.assertTrue(self.app.metacritic)
        self.assertTrue(self.app.currency)
        self.assertTrue(self.app.initial_price)
        self.assertTrue(self.app.final_price)
        self.assertTrue(self.app.discount)

    def test_assign_steam_info_appid(self):
        """ Ensures _assign_json_info() assigns appid. """

        self.app._assign_steam_info(self.response)
        expected_appid = self.response['steam_appid']
        expected_title = self.response['name']
        score = self.response['metacritic']['score']
        desc = self.response['short_description']
        price = self.response['price_overview']['initial']
        fprice = self.response['price_overview']['final']
        cur = self.response['price_overview']['currency']
        expected_date = self.response['release_date']['date']

        self.assertEqual(expected_appid, self.app.appid)
        self.assertEqual(expected_title, self.app.title)
        self.assertEqual(score, self.app.metacritic)
        self.assertEqual(desc, self.app.description)
        self.assertEqual(price, self.app.initial_price)
        self.assertEqual(fprice, self.app.final_price)
        self.assertEqual(cur, self.app.currency)
        self.assertEqual(expected_date, self.app.release_date)

    def test_assign_steam_info_currency_no_price_overview(self):
        """
        Ensure that when the price is not available, price_overview dict is
        not given any values, and hence anything else is not given values, too.
        """

        self.response.pop('price_overview', None)
        self.app._assign_steam_info(self.response)

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

    def test_calculate_price_is_none(self):
        """
        Ensure that when either of the prices is None, 0 is returned:
            - initial price = None -> x$ always has 0% discount from None
            - final price = None -> x$ is always 0% higher than None
        """

        initial = None
        current = 100
        expected = 0
        percent = self.app._calculate_discount(initial, current)

        self.assertEqual(expected, percent)

        initial = 100
        current = None
        expected = 0
        percent = self.app._calculate_discount(initial, current)

        self.assertEqual(expected, percent)


class ScrapingTests(unittest.TestCase):
    """
    Test suite to make sure that web scraping manages to get appropriate
    values (or at least fail gracefully).
    """

    def setUp(self):
        self.app = SteamApp()
        self.app.appid = 1
        self.url = 'http://www.example.com/'

    def test_download_app_html_no_url(self):
        """ Ensure that when appid is not set, nothing is changed. """

        self.url = None
        self.app._download_app_html(self.url)

        self.assertFalse(self.app.recent_count)
        self.assertFalse(self.app.recent_percent)
        self.assertFalse(self.app.overall_count)
        self.assertFalse(self.app.overall_percent)

    @mock.patch('steamCLI.steamapp.Config', autospec=True)
    @mock.patch('steamCLI.steamapp.requests')
    def test_download_app_html_params_requests(self, req, m_config):
        """ Ensure that requests.get() is called with correct parameters. """

        age_key = 'birthtime'
        age_val = 'someval'
        m_config.return_value.get_value.side_effect = [age_key, age_val]
        req.get.return_value = mock.Mock()
        self.app._download_app_html(self.url)

        req.get.assert_called_with(self.url, cookies={age_key: age_val})

    @mock.patch('steamCLI.steamapp.Config', autospec=True)
    @mock.patch('steamCLI.steamapp.requests.get')
    def test_download_app_html_requests_exception(self, get, m_config):
        """
        Ensure that exception is thrown when the app page does not exist.
        """

        m_config.return_value.get_value.side_effect = ['a', 'b']
        mocked_response = mock.Mock()
        mocked_response.raise_for_status.side_effect = HTTPError()
        get.return_value = mocked_response

        with self.assertRaises(HTTPError):
            self.app._download_app_html(self.url)
        m_config.assert_called()
        get.assert_called()

    @mock.patch('steamCLI.steamapp.Config', autospec=True)
    @mock.patch('steamCLI.steamapp.requests.get')
    def test_download_app_html_return_value(self, get, m_config):
        """ Ensures that when everything is ok, string object is returned. """

        text = "pretend this is html"
        m_config.return_value.get_value.side_effect = ['a', 'b']
        mocked_response = mock.Mock()
        mocked_response.text = text
        get.return_value = mocked_response
        actual_text = self.app._download_app_html(self.url)

        self.assertEqual(text, actual_text)
        m_config.assert_called()
        get.assert_called()

    def test_construct_app_steam_page_url_no_url(self):
        """ When there is no appid, url cannot be constructed. """

        self.app.appid = None
        url = self.app._construct_app_url()

        self.assertFalse(url)

    @mock.patch('steamCLI.steamapp.Config', autospec=True)
    def test_construct_app_steam_page_url(self, mock_config):
        """
        When there is app id, there should be no problems constructing it.
        """

        initial_url = 'some/url/[id]/'
        mock_config.return_value.get_value.return_value = initial_url
        expected = initial_url.replace('[id]', '1')
        url = self.app._construct_app_url()

        self.assertEqual(expected, url)
        mock_config.return_value.get_value.assert_called()

    def test_extract_review_text_no_html(self):
        """
        Ensures that undefined html does not break the function.
        """

        html = None
        reviews = self.app._extract_review_text(html)

        self.assertFalse(reviews)

    @mock.patch('steamCLI.steamapp.Config', autospec=True)
    def test_extract_review_text_one_match(self, mock_config):
        """
        Ensures a review text can be extracted from BeautifulSoup.ResultSet.
        Checks what happens when only one match is found (i.e, overall score).
        """

        expected_text = 'get this'
        expected_reviews = [expected_text, ]
        element = 'div'
        class_ = 'test'
        mock_config.return_value.get_value.return_value = [element, class_]

        html = f'''<html>
                     <{element} class="{class_}">
                       {expected_text}
                     </{element}>
                     <{element} class="test2">
                       not this
                     </{element}>
                   </html>'''
        reviews = self.app._extract_review_text(html)

        self.assertEqual(expected_reviews, reviews)

    @mock.patch('steamCLI.steamapp.Config', autospec=True)
    def test_extract_review_text_two_matches(self, mock_config):
        """
        Ensures a review text can be extracted from BeautifulSoup.ResultSet.
        Checks what happens when two matches are found (i.e., overall and
        recent scores).
        """

        expected_text = 'get this'
        other_text = 'and this'
        # As recent reviews are the first ones on Steam page, we want to
        # ensure they are shown last (personal preference)
        expected_reviews = [other_text, expected_text]
        element = 'div'
        class_ = 'test'
        mock_config.return_value.get_value.return_value = [element, class_]

        html = f'''<html>
                     <{element} class="{class_}">
                       {expected_text}
                     </{element}>
                     <{element} class="{class_}">
                       {other_text}
                     </{element}>
                     <{element} class="test2">
                       not this
                     </{element}>
                   </html>'''
        reviews = self.app._extract_review_text(html)

        self.assertEqual(expected_reviews, reviews)

    @mock.patch('steamCLI.steamapp.Config', autospec=True)
    def test_extract_review_text_no_matches(self, mock_config):
        """
        Makes sure that when no matches are found, an empty review list is
        returned.
        """

        element = 'div'
        class_ = 'test'
        mock_config.return_value.get_value.return_value = [element, class_]

        html = f'''<html>
                     <span class="{class_}">
                       no findy
                     </span>
                     <{element} class="irrelevant">
                       no findy
                     </{element}>
                   </html>'''
        reviews = self.app._extract_review_text(html)

        self.assertFalse(reviews)

    def test_extract_app_scores_no_reviews(self):
        """
        Ensure that when no review lines are given function does not break.
        """

        reviews = None
        scores = self.app._extract_app_scores(reviews)

        self.assertFalse(scores)

    def test_extract_app_scores_one_review(self):
        """
        Ensure that with one review line, correct app info is extracted.
        """

        count = '16,855'
        percent = '55%'
        reviews = [f'test test {count} something else {percent}']
        scores = self.app._extract_app_scores(reviews)

        self.assertEqual(count, scores[0][0])
        self.assertEqual(percent, scores[0][1])

    def test_extract_app_scores_two_reviews(self):
        """
        Ensure that with two review lines, correct app info is extracted.
        """

        count1 = '16,855'
        percent1 = '55%'
        count2 = '55,543'
        percent2 = '51%'
        line1 = f'test test {count1} something else {percent1}'
        line2 = f'test test {count2} something else {percent2}'
        reviews = [line1, line2]
        scores = self.app._extract_app_scores(reviews)

        self.assertEqual(count1, scores[0][0])
        self.assertEqual(percent1, scores[0][1])
        self.assertEqual(count2, scores[1][0])
        self.assertEqual(percent2, scores[1][1])

    @mock.patch.object(SteamApp, '_construct_app_url')
    def test_scrape_page_no_appid(self, mock_construct):
        """ Ensures scraping does not begin when no app id is provided. """

        self.app.appid = None
        self.app.scrape_app_page()
        mock_construct.assert_not_called()

    @mock.patch.object(SteamApp, '_construct_app_url')  # a
    @mock.patch.object(SteamApp, '_download_app_html')  # b
    @mock.patch.object(SteamApp, '_extract_review_text')  # c
    @mock.patch.object(SteamApp, '_extract_app_scores')
    def test_scrape_page_two_reviews(self, mock_get_scores, c, b, a):
        """
        Ensures scrape page assigns review scores when two reviews are provided.
        """

        o_count = '1'
        o_percent = '22%'
        r_count = '1'
        r_percent = '45%'
        mock_get_scores.return_value = [(o_count, o_percent),
                                        (r_count, r_percent)]
        self.app.scrape_app_page()

        self.assertEqual(o_count, self.app.overall_count)
        self.assertEqual(o_percent, self.app.overall_percent)
        self.assertEqual(r_count, self.app.recent_count)
        self.assertEqual(r_percent, self.app.recent_percent)

    @mock.patch.object(SteamApp, '_construct_app_url')  # a
    @mock.patch.object(SteamApp, '_download_app_html')  # b
    @mock.patch.object(SteamApp, '_extract_review_text')  # c
    @mock.patch.object(SteamApp, '_extract_app_scores')
    def test_scrape_page_one_review(self, mock_get_scores, c, b, a):
        """
        Ensures scrape page assigns review scores when one review is provided.
        """

        o_count = '1'
        o_percent = '22%'
        mock_get_scores.return_value = [(o_count, o_percent), ]
        self.app.scrape_app_page()

        self.assertEqual(o_count, self.app.overall_count)
        self.assertEqual(o_percent, self.app.overall_percent)
        self.assertFalse(self.app.recent_count)
        self.assertFalse(self.app.recent_percent)

    @mock.patch.object(SteamApp, '_construct_app_url')  # a
    @mock.patch.object(SteamApp, '_download_app_html')  # b
    @mock.patch.object(SteamApp, '_extract_review_text')  # c
    @mock.patch.object(SteamApp, '_extract_app_scores')
    def test_scrape_page_no_reviews(self, mock_get_scores, c, b, a):
        """
        Ensures scrape page assigns review scores when one review is provided.
        """

        mock_get_scores.return_value = list()
        self.app.scrape_app_page()

        self.assertFalse(self.app.overall_count)
        self.assertFalse(self.app.overall_percent)
        self.assertFalse(self.app.recent_count)
        self.assertFalse(self.app.recent_percent)


class IsThereAnyDealAPITests(unittest.TestCase):
    """
    Test suite for functionality that relies on data from Is There Any
    Deal API.
    """

    def setUp(self):
        self.app = SteamApp()

    def test_construct_itad_url_no_title(self):
        """
        Ensures that url is not constructed when a title is missing (since it
        is a key parameter and without it url is invalid).
        """

        url = self.app._construct_itad_url(region='uk')

        self.assertFalse(url)

    @mock.patch('steamCLI.steamapp.Config', autospec=True)
    def test_construct_itad_url_no_region(self, mocked_config):
        """ Ensure that given no region, default is used. """

        self.app.title = 'test'
        region = 'uk'
        mock_url = 'www.example.com/mock/url/[region]'
        mock_url_region = mock_url.replace('[region]', region)
        mock_key = 'mock_key'
        mocked_config.return_value.get_value.side_effect = [region, mock_url,
                                                            mock_key]
        url = self.app._construct_itad_url(region='')

        self.assertEqual(url, mock_url_region)

    


