# To run single test module:
# >>> python -m unittest test.test_some_module

import unittest

from unittest import mock
from requests import HTTPError

from steamCLI.steamapp import SteamApp
from steamCLI.config import Config

# Stubs that tests can use.
RESOURCE = '{"applist": {"apps": {"app": [{"appid": 8,"name": "winui2"}]}}}'
MOCK_DICT = {"appid": 8, "name": "winui2"}
MOCK_DATA = {"8": {"success": True, "data": {}}}


class SteamAppConstructionTests(unittest.TestCase):
    """ Ensures SteamApp can be properly initialized. """

    def test_should_raise_FileNotFoundError(self):
        """
        Ensures that SteamApp cannot be initialised without a
        valid config, as it is a cornerstone of the app.
        """

        with self.assertRaises(FileNotFoundError):
            SteamApp(config=None)



class SteamAppFetchTextAssignIDTests(unittest.TestCase):
    """ Tests related to functionality necessary to find app id. """

    def setUp(self):
        self.url = 'http://api.example.com/test/'
        self.title = MOCK_DICT["name"]
        self.appid = MOCK_DICT["appid"]
        self.config = mock.Mock(Config)
        self.app = SteamApp(self.config)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_should_raise_error_upon_inaccessible_resource(self, mock_get):
        """ Ensures an error is thrown if resource cannot be accessed. """

        mocked_response = mock.Mock()
        mocked_response.raise_for_status.side_effect = HTTPError()
        mock_get.return_value = mocked_response

        with self.assertRaises(HTTPError):
            self.app._fetch_resource(self.url)
        mock_get.assert_called_once_with(self.url)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_should_fetch_resource_when_it_exists(self, mock_get):
        """ Ensures json can be requested instead of textual repr. """

        mock_obj = mock.Mock()
        mock_obj.json.return_value = MOCK_DATA
        mock_get.return_value = mock_obj
        actual = self.app._fetch_resource(self.url, text=False)

        self.assertEqual(MOCK_DATA, actual)
        mock_get.assert_called_once_with(self.url)
        mock_obj.json.assert_called_once()

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_should_fetch_resource_if_it_exists_in_textual_form(self, mock_get):
        """ Ensures a textual repr. is returned if resource can be accessed. """

        mock_get.return_value = mock.MagicMock(text=RESOURCE)
        actual = self.app._fetch_resource(self.url)

        self.assertEqual(RESOURCE, actual)
        self.assertIn(mock.call(self.url), mock_get.call_args_list)

    @mock.patch.object(SteamApp, '_pick_complete_json')
    def test_should_not_extract_app_dictionary_when_no_such_app(self, m_func):
        """ Ensures that when nothing is found, None is returned. """

        m_func.return_value = None
        self.app.title = "Test"
        result = self.app._extract_app_dictionary(RESOURCE)

        self.assertFalse(result)
        m_func.assert_called_once()

    @mock.patch.object(SteamApp, '_pick_complete_json')
    def test_should_extract_relevant_app_data(self, mock_choose):
        """
        Ensures _extract_app_dictionary() manages to find relevant dictionaries.
        """

        mock_choose.return_value = MOCK_DATA
        result = self.app._extract_app_dictionary(RESOURCE, title=self.title)

        self.assertEqual(MOCK_DATA, result)
        mock_choose.assert_called_once()

    @mock.patch.object(SteamApp, '_pick_complete_json')
    def test_should_extract_app_dictionary_case_insensitive(self, mock_choose):
        """ Ensure that _extract_app_dictionary() is not case sensitive. """

        mock_choose.return_value = MOCK_DATA
        upper_title = self.title.upper()
        result = self.app._extract_app_dictionary(RESOURCE, title=upper_title)

        self.assertEqual(MOCK_DATA, result)
        mock_choose.assert_called_once()

    @mock.patch.object(SteamApp, '_pick_complete_json')
    def test_should_extract_app_dictionary_given_id(self, mock_choose):
        """
        Ensure that _extract_app_dictionary() works not only with title, but with
        app id as well.
        """

        mock_choose.return_value = MOCK_DATA
        result = self.app._extract_app_dictionary(RESOURCE, app_id=self.appid)

        self.assertEqual(MOCK_DATA, result)
        mock_choose.assert_called_once()

    @mock.patch.object(SteamApp, '_pick_complete_json')
    def test_should_not_get_app_dict_with_id_when_no_such_id(self, mock_choose):
        """ Ensure that when the ID is wrong, nothing is found. """

        mock_choose.return_value = None
        result = self.app._extract_app_dictionary(RESOURCE, app_id=0)

        self.assertFalse(result)
        mock_choose.assert_called_once()

    @mock.patch.object(SteamApp, '_fetch_resource')
    @mock.patch.object(SteamApp, '_extract_app_dictionary')
    @mock.patch.object(SteamApp, '_assign_steam_info')
    def test_should_find_app_given_valid_title(self, m_assign, m_extr, m_fetch):
        """
        Ensures that an app can be found when a valid resource and a valid app
        title is provided.
        """

        m_fetch.return_value = RESOURCE
        m_extr.return_value = MOCK_DATA
        self.app.find_app(self.url, title=self.title)

        m_fetch.assert_called_once_with(self.url)
        m_assign.assert_called_once_with(MOCK_DATA)
        m_extr.assert_called_once_with(RESOURCE, app_id=None, region=None,
                                       title=self.title)

    @mock.patch.object(SteamApp, '_fetch_resource')
    @mock.patch.object(SteamApp, '_extract_app_dictionary')
    @mock.patch.object(SteamApp, '_assign_steam_info')
    def test_should_find_app_given_id(self, m_assign, m_extr, m_fetch):
        """
        Ensures that an app can be found when a valid resource and a valid
        app id is provided.
        """

        m_fetch.return_value = RESOURCE
        m_extr.return_value = MOCK_DATA
        self.app.find_app(self.url, app_id=self.appid)

        m_fetch.assert_called_once_with(self.url)
        m_assign.assert_called_once_with(MOCK_DATA)
        m_extr.assert_called_once_with(RESOURCE, app_id=self.appid,
                                       region=None, title=None)

    @mock.patch.object(SteamApp, '_fetch_resource')
    @mock.patch.object(SteamApp, '_extract_app_dictionary')
    @mock.patch.object(SteamApp, '_assign_steam_info')
    def test_should_not_find_app_with_no_data(self, m_assign, m_get, m_fetch):
        """ Ensures that ID is not found with an invalid resource. """

        m_fetch.return_value = RESOURCE
        m_get.return_value = None
        self.app.find_app(self.url)

        m_fetch.assert_called_once_with(self.url)
        m_assign.assert_called_once_with(None)
        m_get.assert_called_once_with(RESOURCE, app_id=None, region=None,
                                      title=None)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_should_choose_json_with_success_true(self, mock_get):
        """
        Ensures that _choose_one() method returns a JSON info that has
        success set as true. If no such dictionary exists, then it
        should return None.
        """

        self.config.get_value.side_effect = ["doesn't matter", "doesn't matter"]
        # Dictionaries that we get from a list of all apps
        # (http://api.steampowered.com/ISteamApps/GetAppList/v0002/)
        dict_list = [{"appid": 1, "name": "test"},
                     {"appid": 2, "name": "test"},
                     {"appid": 3, "name": "test"}]
        # Stub dictionary similar to what we get accessing individual apps
        # E.g.: http://store.steampowered.com/api/appdetails?appids=10
        fake_r1 = mock.Mock()
        fake_r2 = mock.Mock()
        fake_r3 = mock.Mock()
        fake_r1.json.return_value = {"1": {"success": False}}
        fake_r2.json.return_value = {"2": {"success": False}}
        fake_r3.json.return_value = {"3": {"success": True,
                                           "data": {"test": {}}}}
        mock_get.side_effect = [fake_r1, fake_r2, fake_r3]
        json_data = self.app._pick_complete_json(dict_list)

        fake_r1.json.assert_called_once()
        fake_r2.json.assert_called_once()
        fake_r3.json.assert_called_once()
        # _pick_complete_json() returns only relevant data, hence keys.
        self.assertEqual(
            {"3": {"success": True, "data": {"test": {}}}}["3"]["data"], json_data)
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)
        mock_get.assert_called()
        # 2 False, 1 (last) True, hence 3 calls.
        self.assertEqual(mock_get.call_count, 3)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_should_choose_first_true_json(self, mock_get):
        """
        Ensures that _choose_one() method returns a JSON info that has
        success set as true. If no such dictionary exists, then it
        should return None.
        """

        self.config.get_value.side_effect = ["doesn't matter", "doesn't matter"]
        # Dictionaries that we get from a list of all apps
        # (http://api.steampowered.com/ISteamApps/GetAppList/v0002/)
        dict_list = [{"appid": 1, "name": "test"},
                     {"appid": 2, "name": "test"},
                     {"appid": 3, "name": "test"}]
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
        json_data = self.app._pick_complete_json(dict_list)

        fake_r1.json.assert_called_once()
        fake_r2.json.assert_called_once()
        fake_r3.json.assert_not_called()  # Does not reach this one
        self.assertEqual(app_d2["2"]["data"], json_data)
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)
        mock_get.assert_called()
        # Second dictionary has True value, hence the third one is not reached.
        self.assertEqual(mock_get.call_count, 2)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_should_not_choose_json_when_all_false(self, mock_get):
        """
        Ensures that when dicts passed do not have 'success: True' None is
        returned.
        """

        self.config.get_value.side_effect = ["doesn't matter", "doesn't matter"]
        dict_list = [{"appid": 1, "name": "test"}, ]
        fake_response = mock.Mock()
        fake_response.json.return_value = {"1": {"success": False}}
        mock_get.return_value = fake_response
        json_data = self.app._pick_complete_json(dict_list)

        fake_response.json.assert_called_once()
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)
        self.assertFalse(json_data)

    def test_should_not_do_anything_when_empty_list_is_given(self):
        """ Ensure empty list does not break the function. """

        empty_list = []
        json_data = self.app._pick_complete_json(empty_list)

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
    #     self.assertEqual(expected_id, app.appID)


class SteamAppAssignInfoTests(unittest.TestCase):
    """
    Tests related to functionality necessary for assignment of values to
    various fields, such as title, price, metacritic score info, etc.
    """

    def setUp(self):
        self.id = 1
        self.url = 'http://api.example.com/test/'
        self.app = SteamApp(config="stubConfig")
        self.app.appID = self.id

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

    def test_should_return_matching_values(self):
        """
        Ensures that _get_value() returns appropriate values given correct key.
        """

        key = 'steam_appid'
        value = self.app._get_value(self.response, key)

        self.assertEqual(self.response[key], value)

    def test_should_return_none_with_incorrect_key(self):
        """
        Ensures that even when incorrect/non-existent key is supplied,
        none is returned.

        Explanation: Steam's JSON is inconsistent and some games do not
        necessarily have some of the usual information.
        """

        value = self.app._get_value(json_data=self.response,
                                    key='detailed_description')

        self.assertFalse(value)

    def test_should_get_nested_value(self):
        """
        Ensures that _get_nested_value() returns appropriate values given
        correct keys.
        """

        outer_key = 'price_overview'
        inner_key = 'currency'
        value = self.app._get_nested_value(self.response, outer_key, inner_key)

        self.assertEqual(self.response[outer_key][inner_key], value)

    def test_should_return_none_when_outer_key_nonexistent(self):
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

    def test_should_return_none_when_inner_key_nonexistent(self):
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

    def test_should_assign_steam_info_given_correct_data(self):
        """ Tests whether the function works given correct data. """

        self.app._assign_steam_info(self.response)

        self.assertTrue(self.app.release_date)
        self.assertTrue(self.app.description)
        self.assertTrue(self.app.metacritic)
        self.assertTrue(self.app.currency)
        self.assertTrue(self.app.initial_price)
        self.assertTrue(self.app.final_price)
        self.assertTrue(self.app.discount)

    def test_should_assign_information(self):
        """ Ensures _assign_json_info() assigns all kinds of info. """

        self.app._assign_steam_info(self.response)
        expected_app_id = self.response['steam_appid']
        expected_title = self.response['name']
        score = self.response['metacritic']['score']
        description = self.response['short_description']
        price = self.response['price_overview']['initial']
        final_price = self.response['price_overview']['final']
        currency = self.response['price_overview']['currency']
        expected_date = self.response['release_date']['date']

        self.assertEqual(expected_app_id, self.app.appID)
        self.assertEqual(expected_title, self.app.title)
        self.assertEqual(score, self.app.metacritic)
        self.assertEqual(description, self.app.description)
        self.assertEqual(price, self.app.initial_price)
        self.assertEqual(final_price, self.app.final_price)
        self.assertEqual(currency, self.app.currency)
        self.assertEqual(expected_date, self.app.release_date)

    def test_should_not_assign_currency_when_no_price_overview(self):
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


class ScrapingTests(unittest.TestCase):
    """
    Test suite to make sure that web scraping manages to get appropriate
    values (or at least fail gracefully).
    """

    def setUp(self):
        self.config = mock.Mock(Config)
        self.app = SteamApp(self.config)
        self.app.appID = 1
        self.url = 'http://www.example.com/'

    def test_should_not_download_app_html_when_no_url(self):
        """ Ensure that when url is not given, nothing is changed. """

        self.url = None
        self.app._download_app_html(self.url)

        self.assertFalse(self.app.recent_count)
        self.assertFalse(self.app.recent_percent)
        self.assertFalse(self.app.overall_count)
        self.assertFalse(self.app.overall_percent)

    @mock.patch('steamCLI.steamapp.requests')
    def test_should_call_with_correct_params(self, req):
        """ Ensure that requests.get() is called with correct parameters. """

        age_key = 'birth time'
        age_val = 'some val'
        self.config.get_value.side_effect = [age_key, age_val]
        req.get.return_value = mock.Mock()
        self.app._download_app_html(self.url)

        req.get.assert_called_once_with(self.url, cookies={age_key: age_val})
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_should_throw_exception_when_page_non_existent(self, get):
        """
        Ensure that exception is thrown when the app page does not exist.
        """

        mocked_response = mock.Mock()
        mocked_response.raise_for_status.side_effect = HTTPError()
        get.return_value = mocked_response

        with self.assertRaises(HTTPError):
            self.app._download_app_html(self.url)
        get.assert_called_once()
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)

    @mock.patch('steamCLI.steamapp.requests.get')
    def test_should_return_string_value(self, get):
        """ Ensures that when everything is ok, string object is returned. """

        text = "pretend this is html"
        key = 'test_age_key'
        value = 'test_age_value'
        self.config.get_value.side_effect = [key, value]
        mocked_response = mock.Mock()
        mocked_response.text = text
        get.return_value = mocked_response
        actual_text = self.app._download_app_html(self.url)

        self.assertEqual(text, actual_text)
        get.assert_called_with(self.url, cookies={key: value})
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)

    def test_should_not_construct_app_steam_page_url_when_no_app_id(self):
        """ When there is no app_id, url cannot be constructed. """

        self.app.appID = None
        url = self.app._construct_app_url()

        self.assertFalse(url)

    def test_should_construct_app_url_when_valid_id(self):
        """
        When there is app id, there should be no problems constructing it.
        """

        initial_url = 'some/url/[id]/'
        self.config.get_value.return_value = initial_url
        expected = initial_url.replace('[id]', str(self.app.appID))
        url = self.app._construct_app_url()

        self.assertEqual(expected, url)
        self.config.get_value.assert_called_once()

    def test_should_not_extract_review_text_when_no_html(self):
        """
        Ensures that undefined html does not break the function.
        """

        reviews = self.app._extract_review_text(html=None)

        self.assertFalse(reviews)

    def test_should_extract_review_text_with_one_match(self):
        """
        Ensures a review text can be extracted from BeautifulSoup.ResultSet.
        Checks what happens when only one match is found (i.e, overall score).
        """

        expected_text = 'get this'
        expected_reviews = [expected_text, ]
        element = 'div'
        class_ = 'test'
        self.config.get_value.side_effect = [element, class_]

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
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)

    def test_should_extract_review_text_with_two_matches(self):
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
        self.config.get_value.side_effect = [element, class_]

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
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)

    def test_should_not_extract_review_text_with_no_matches(self):
        """
        Makes sure that when no matches are found, an empty review list is
        returned.
        """

        element = 'div'
        class_ = 'test'
        self.config.get_value.side_effect = [element, class_]

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
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)

    def test_should_not_extract_app_scores_wit_no_reviews(self):
        """
        Ensure that when no review lines are given function does not break.
        """

        scores = self.app._extract_app_scores(reviews=None)

        self.assertFalse(scores)

    def test_should_extract_app_scores_with_one_review(self):
        """
        Ensure that with one review line, correct app info is extracted.
        """

        count = '16,855'
        percent = '55%'
        reviews = [f'test test {count} something else {percent}']
        scores = self.app._extract_app_scores(reviews)

        self.assertEqual(count, scores[0][0])
        self.assertEqual(percent, scores[0][1])

    def test_should_extract_app_scores_with_two_reviews(self):
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
    def test_should_not_crape_page_with_no_appid(self, mock_construct):
        """ Ensures scraping does not begin when no app id is provided. """

        self.app.appID = None
        self.app.scrape_app_page()
        mock_construct.assert_not_called()

    @mock.patch.object(SteamApp, '_construct_app_url')  # a
    @mock.patch.object(SteamApp, '_download_app_html')  # b
    @mock.patch.object(SteamApp, '_extract_review_text')  # c
    @mock.patch.object(SteamApp, '_extract_app_scores')
    def test_should_scrape_page_with_two_reviews(self, m_get_scores, c, b, a):
        """
        Ensures scrape page assigns review scores when two reviews are provided.
        """

        o_count = '1'  # Overall
        o_percent = '22%'
        r_count = '1'  # Recent
        r_percent = '45%'
        m_get_scores.return_value = [(o_count, o_percent), (r_count, r_percent)]
        self.app.scrape_app_page()

        self.assertEqual(o_count, self.app.overall_count)
        self.assertEqual(o_percent, self.app.overall_percent)
        self.assertEqual(r_count, self.app.recent_count)
        self.assertEqual(r_percent, self.app.recent_percent)
        m_get_scores.assert_called_once()
        c.assert_called_once()
        b.assert_called_once()
        a.assert_called_once()

    @mock.patch.object(SteamApp, '_construct_app_url')  # a
    @mock.patch.object(SteamApp, '_download_app_html')  # b
    @mock.patch.object(SteamApp, '_extract_review_text')  # c
    @mock.patch.object(SteamApp, '_extract_app_scores')
    def test_should_scrape_page_with_one_review(self, mock_get_scores, c, b, a):
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
        mock_get_scores.assert_called_once()
        c.assert_called_once()
        b.assert_called_once()
        a.assert_called_once()

    @mock.patch.object(SteamApp, '_construct_app_url')  # a
    @mock.patch.object(SteamApp, '_download_app_html')  # b
    @mock.patch.object(SteamApp, '_extract_review_text')  # c
    @mock.patch.object(SteamApp, '_extract_app_scores')
    def test_should_not_scrape_page_no_reviews(self, mock_get_scores, c, b, a):
        """
        Ensures scrape page does not assign any information when no reviews
        are found.
        """

        mock_get_scores.return_value = list()
        self.app.scrape_app_page()

        self.assertFalse(self.app.overall_count)
        self.assertFalse(self.app.overall_percent)
        self.assertFalse(self.app.recent_count)
        self.assertFalse(self.app.recent_percent)
        mock_get_scores.assert_called_once()
        c.assert_called_once()
        b.assert_called_once()
        a.assert_called_once()


class IsThereAnyDealAPITests(unittest.TestCase):
    """
    Test suite for functionality that relies on data from Is There Any
    Deal API.
    """

    def setUp(self):
        self.config = mock.Mock(Config)
        self.app = SteamApp(self.config)

    def test_should_create_url_with_default_region_with_missing(self):
        """ Ensure that given no region, default is used. """

        region = 'uk'
        mock_key = 'mock_key'
        mock_url = 'www.example.com/mock/url/[region]'
        mock_url_region = mock_url.replace('[region]', region)
        self.config.get_value.side_effect = [region, mock_key, mock_url]
        url = self.app._construct_itad_url("test", region='')

        self.assertEqual(mock_url_region, url)
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 3)

    def test_should_construct_proper_url_with_given_title(self):
        """
        Ensure a url is constructed properly - title is in lower case,
        etc - when _construct_itad_url is called.
        """

        title = "test_title"
        mock_url = 'www.example.com/mock/url/[title]'
        mock_url_title = mock_url.replace('[title]', title)
        self.config.get_value.side_effect = ['mock_key', mock_url]
        url = self.app._construct_itad_url(title, region="eu")

        self.assertEqual(mock_url_title, url)
        self.config.get_value.assert_called()
        self.assertEqual(self.config.get_value.call_count, 2)

    # @mock.patch('steamCLI.steamapp.Config', autospec=True)  # left as example
    # def test_should_construct_url_with_given_key(self, mocked_config):
    def test_should_construct_url_with_given_key(self):
        """
        Ensure that the key is replaced when _construct_itad_url is called.
        """

        mock_key = 'mock_key'
        mock_url = 'www.example.com/mock/url/[key]'
        mock_url_title = mock_url.replace('[key]', mock_key)
        self.config.get_value.side_effect = [mock_key, mock_url]
        url = self.app._construct_itad_url("placeholder", region="eu")

        self.assertEqual(mock_url_title, url)
        self.assertEqual(self.config.get_value.call_count, 2)
    
    def test_should_not_extract_historical_low_wit_no_title(self):
        """ Ensure that with no title historical low cannot be extracted. """

        self.app.title = None
        self.app.extract_historical_low(region="test region")

        self.assertFalse(self.app.historical_low)
        self.assertFalse(self.app.historical_shop)
        self.assertFalse(self.app.historical_cut)

    @mock.patch.object(SteamApp, '_construct_itad_url')
    @mock.patch.object(SteamApp, '_fetch_resource')
    def test_should_assigns_values_with_correct_json(self, m_fetch, m_url):
        """ Ensure the method works when a proper JSON is returned. """

        app_title = 'test_title'
        expected_cut = 50
        expected_price = 1
        expected_shop_name = 'test_shop'
        self.app.title = app_title
        m_url.return_value = "doesn't matter"
        m_fetch.return_value = {
            'data': {
                app_title.replace('_', ''): {
                    'cut': expected_cut,
                    'price': expected_price,
                    'shop': {
                        'name': expected_shop_name,
                    }}}}

        self.app.extract_historical_low(region='uk')

        self.assertEqual(expected_cut, self.app.historical_cut)
        self.assertEqual(expected_shop_name, self.app.historical_shop)
        self.assertEqual(expected_price, self.app.historical_low)
        m_fetch.assert_called_once()
        m_url.assert_called_once_with(app_title.replace('_', ''), 'uk')
