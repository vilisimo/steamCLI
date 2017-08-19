import json
from typing import List, Union

import os
import requests
from bs4 import BeautifulSoup

from steamCLI.utils import sanitize_title, calculate_discount


class SteamApp:
    def __init__(self, config=None):
        """
        Values shown for clarity. In an ideal case, we aim to assign
        values to all of them.
        """

        if not config:
            raise FileNotFoundError("Configuration file was not found.")

        self.config = config

        # Key information
        self.title, self.appID = [None] * 2
        # Additional game information
        self.release_date, self.description, self.metacritic = [None]*3
        # Pricing information
        self.currency, self.initial_price, self.final_price = [None]*3
        self.discount = None
        # Review information
        self.overall_count, self.overall_percent = [None]*2
        self.recent_count, self.recent_percent = [None]*2
        # Historical low
        self.historical_low, self.historical_cut = [None]*2
        self.historical_shop = None

    def find_app(self, origin: str, title: str=None, app_id: int=None,
                 region: str=None):
        """
        Finds an app corresponding to a given title/id. Assigns the object
        information corresponding to the apps.

        Does so by calling helper methods which (roughly) do the following:
            * Check if the title/id is in the list of all steam apps 
            * If it is, return json data about the app 
            * Inspect the data to find information about the app
            * Use it to set object attributes

        :param origin: url to resource: where a list of games is located.
        :param title: title of an app that needs to be checked.
        :param app_id: id of an app that needs to be checked.
        :param region: region for which the information should be retrieved.
        """

        text = self._fetch_resource(origin)
        app_data = self._extract_app_dictionary(text, title=title, app_id=app_id,
                                                region=region)
        self._assign_steam_info(app_data)

    @staticmethod
    def _fetch_resource(origin: str, text: bool=True) -> Union[str, dict]:
        """
        Gets the textual JSON representation from a given link.

        :param origin: link to a resource.
        :param text: determines what should be returned: json or text.
        """

        try:
            response = requests.get(origin)
            response.raise_for_status()
        except requests.HTTPError:
            raise requests.HTTPError("Resource not found.")
        else:
            if text:
                return response.text
            else:
                return response.json()

    def _extract_app_dictionary(self, json_text: str, title: str=None,
                                app_id: int=None, region: str=None) -> dict:
        """
        Extracts dict in which app resides from JSON response by loading textual
        representation of JSON and applying private inner function to it over
        and over again.

        :param json_text: textual representation of JSON object.
        :param title: title of the to-be-found app
        :param app_id: id of the to-be-found app
        :param region: region for which the data should be fetched
        :return: dictionary that has the relevant information about an app.
        """

        app_dicts = []

        def _decode_dictionary(dictionary: dict) -> dict:
            """
            Search for key with "name" value that == target application name.
            If found, it means the dictionary is the one we are interested in.

            :param dictionary: app dictionary (i.e. {"appid": int, "name": str})
            """

            try:
                if title:
                    if dictionary["name"].lower() == title.lower():
                        app_dicts.append(dictionary)
                else:
                    if dictionary["appid"] == app_id:
                        app_dicts.append(dictionary)
            except KeyError:
                pass
            return dictionary

        json.loads(json_text, object_hook=_decode_dictionary)
        json_data = self._pick_complete_json(app_dicts, region=region)

        return json_data

    def _pick_complete_json(self, dicts: List[dict], region: str=None) -> dict:
        """
        Goes through dictionaries to an app that can be consumed successfully.

        That is, sometimes in Steam app list apps have identical names and
        querying API* with corresponding ids does not give any information
        back.

        E.g., there are 3 dictionaries that have their title as "Borderlands",
        with corresponding IDs as 8950, 8980 and 8989. However, only 8980
        responds to queries. All others return {"[appid]":{"success":false}},
        which is not useful. Unfortunately, it is impossible to know which
        one will return a useful response (at least without resorting to 3rd
        party APIs). Hence, in the worst case, each and every one of dicts will
        have to be checked, potentially slowing the application significantly.

        *http://store.steampowered.com/api/appdetails?appids=id

        :param dicts: app dicts to be checked. Typical input:
                      {"appid": int, "name": str}
        :param region: region for which the information should be retrieved.
        :return: JSON of successful query (i.e., dictionary with app info)
        """

        if dicts:
            base_url = self.config.get_value('SteamAPIs', 'appinfo')
            if not region:
                region = self.config.get_value('SteamRegions', 'default')
            for d in dicts:
                appid = d['appid']
                resource = f'{base_url}{appid}&cc={region}'
                response = requests.get(resource)
                data = response.json()
                if data[str(appid)]['success']:
                    return data[str(appid)]['data']

    def _assign_steam_info(self, app_data: dict=None):
        """
        Retrieves and assigns information about an app to the object.

        :param app_data: dictionary from steam api that contains data on app
        """

        if not app_data:
            return

        self.appID = self._get_value(app_data, 'steam_appid')
        self.title = self._get_value(app_data, 'name')
        self.release_date = self._get_nested_value(app_data, 'release_date',
                                                   'date')
        self.description = self._get_value(app_data, 'short_description')
        self.metacritic = self._get_nested_value(app_data, 'metacritic',
                                                 'score')
        self.currency = self._get_nested_value(app_data, 'price_overview',
                                               'currency')
        self.initial_price = self._get_nested_value(app_data, 'price_overview',
                                                    'initial')
        self.final_price = self._get_nested_value(app_data, 'price_overview',
                                                  'final')
        self.discount = calculate_discount(self.initial_price, self.final_price)

    def scrape_app_page(self):
        """
        Scrapes app page for information on reviews and how many of them were
        positive.
        """

        if not self.appID:
            return

        url = self._construct_app_url()
        html = self._download_app_html(url)
        reviews = self._extract_review_text(html)
        scores = self._extract_app_scores(reviews)

        if scores:
            overall = scores[0]
            self.overall_count = overall[0]
            self.overall_percent = overall[1]
        if len(scores) > 1:
            recent = scores[1]
            self.recent_count = recent[0]
            self.recent_percent = recent[1]

    def _construct_app_url(self) -> str:
        """
        Constructs steam page URL that is used for web scraping.

        :return: app url with an assigned id
        """

        if not self.appID:
            return ''

        app_url = self.config.get_value('SteamWebsite', 'app_page')
        url = app_url.replace('[id]', str(self.appID))

        return url

    def _download_app_html(self, url: str) -> str:
        """
        Scrapes review scores from the app's Steam page.

        :param url: url which will be used to retrieve app html.
        :return: html (string) of the whole page.
        """

        if not url:
            return ''

        age_key = self.config.get_value('SteamWebsite', 'age_key')
        age_value = self.config.get_value('SteamWebsite', 'age_value')
        age_cookie = {age_key: age_value}

        try:
            response = requests.get(url, cookies=age_cookie)
            response.raise_for_status()
        except requests.HTTPError:
            raise requests.HTTPError("App page not found.")
        else:
            return response.text

    def _extract_review_text(self, html: str) -> List[str]:
        """
        Extracts recent/overall review text (lines) from html.

        First, we get the elements and their classes, so we know what to
        search for. Then, we comb that document to find all elements that
        match our criteria. This results in a list of ResultSet objects.
        Each of these objects has children, over which we can iterate (e.g.,
        by calling next(iterable) or simple for loops). Since reviews have a
        lot of whitespace applied to them, we need to remove it. Once we do
        it, we can return a list of review lines, so that it can be processed
        further or used as is.

        :param html: html of the page to be parsed.
        :return: list of review lines.
        """

        reviews = list()

        if not html:
            return reviews

        element = self.config.get_value('SteamWebsite', 'reviews_element')
        classes = self.config.get_value('SteamWebsite', 'reviews_class')
        app_page = BeautifulSoup(html, "html.parser")
        results = app_page.findAll(element, {'class': classes})

        # Results might be empty. This is fine = app does not have any reviews.
        while results:
            result = results.pop()  # This way recent is last.
            review = ''.join(child.strip() for child in result.children)
            reviews.append(review)

        return reviews

    @staticmethod
    def _extract_app_scores(reviews: List[str]) -> List[str]:
        """
        Extracts scores from review line(s).

        :param reviews: list of review lines.
        :return: list of score tuples:
                    [0]: overall reviews (count, percentage)
                    [1]: recent reviews (count, percentage)
        """

        scores = list()

        if not reviews:
            return scores

        while reviews:
            line = reviews.pop(0)
            tokens = line.split()
            # Usually they are at positions 1 and 4, but why take chances.
            # For different sep., may need re.sub(r'[^\w\s]', '', t) or similar
            count = [t for t in tokens if t.replace(',', '').isdigit()][0]
            percent = [t for t in tokens if t.endswith('%')][0]
            scores.append((count, percent))

        return scores

    def extract_historical_low(self, region: str):
        """ 
        Extracts historical low price by calling Is There Any Deal API.

        :param region: which region should the price be found for.
        """

        if not self.title:
            return

        sanitized_title = sanitize_title(self.title)
        url = self._construct_itad_url(sanitized_title, region)
        itad_json = self._fetch_resource(url, text=False)
        itad_data = itad_json['data'][sanitized_title]
        self.historical_cut = self._get_value(itad_data, 'cut')
        self.historical_low = self._get_value(itad_data, 'price')
        self.historical_shop = self._get_nested_value(itad_data, 'shop', 'name')

    def _construct_itad_url(self, sanitized_title: str, region: str):
        """
        Constructs url conforming to ITAD expectation.

        :param region: which region should be used to query ITAD.
        """

        if not region:
            region = self.config.get_value('SteamRegions', 'default')

        env_var = self.config.get_value('IsThereAnyDealAPI', 'env_var')
        api_key = self._retrieve_api_key(env_var)
        app_url = self.config.get_value('IsThereAnyDealAPI', 'app_url')
        url = (app_url.replace('[region]', region)
                      .replace('[key]', api_key)
                      .replace('[title]', sanitized_title))
        return url

    @staticmethod
    def _retrieve_api_key(env_var):
        try:
            return os.environ[env_var]
        except KeyError:
            raise KeyError("Environment variable not found")

    @staticmethod
    def _get_value(json_data: dict, key: str) -> str:
        """
        Gets a key value from a given JSON.

        As Steam's JSON data is inconsistent, it might very well miss some of
        the things that are usually present in other apps. Hence, we simply
        set the value to None instead of reporting the problem, as this is
        (albeit rare) expected occurrence.

        :param json_data: dictionary which is to be inspected for a key-value.
        :param key: dictionary key for which the value should be returned.
        :return: value corresponding to a key.
        """

        try:
            value = json_data[key]
        except KeyError:
            value = None
        return value

    @staticmethod
    def _get_nested_value(json_data: dict,
                          outer_key: str,
                          inner_key: str) -> Union[str, int]:
        """
        Gets a specified value from a given JSON.

        Information in Steam's response is not always 'flat'. it often
        contains nested dictionaries, e.g. 'price_overview': {...}. Most of
        the time, however, depth is limited to two levels.

        :param json_data: dictionary which is to be inspected for a key-value.
        :param outer_key: key to get an inner dictionary.
        :param inner_key: key to get a value from the inner dictionary.
        :return: value corresponding to a key in the inner dictionary.
        """

        if outer_key not in json_data:
            return None
        if inner_key not in json_data[outer_key]:
            return None

        return json_data[outer_key][inner_key]
