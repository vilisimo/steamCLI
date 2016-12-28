import requests
import json

from steamCLI.config import Config


class SteamApp:
    def __init__(self):
        """
        Values shown only for readability. In the ideal case, we aim to assign
        values to all of them.
        """

        # Key information
        self.title, self.appid = [None]*2
        # Additional game information
        self.release_date, self.description, self.metascore = [None]*3
        # Pricing information
        self.currency, self.initial_price, self.final_price = [None]*3
        self.discount = None

    def find_app(self, origin, title=None, appid=None, region=None):
        """
        Finds an app corresponding to a given title/id. Assigns the object
        information corresponding to the apps.

        Does so by calling helper methods which (roughly) do the following:
        check if the title/id is in the list of all steam apps. If it is,
        return json data about the app. Then, inspect this data to find
        information about the app, and use it to set object attributes.

        :param origin: url to resource: where a list of games is located.
        :param title: title of an app that needs to be checked.
        :param appid: id of an app that needs to be checked.
        :param region: region for which the information should be retrieved.
        """

        text = self._fetch_text(origin)
        app_data = self._get_app_data(text, title=title, appid=appid,
                                      region=region)
        self._assign_steam_info(app_data)

    def _assign_steam_info(self, app_data=None):
        """ Retrieves and assigns information about an app to the object. """

        if not app_data:
            return

        # steam_url = self._get_steam_app_url(region)
        # app_data = self._fetch_json(steam_url)

        # Field assignment
        self.appid = self._get_appid(app_data)
        self.title = self._get_title(app_data)
        self.release_date = self._get_release_date(app_data)
        self.description = self._get_description(app_data)
        self.metascore = self._get_metascore(app_data)

        price_dict = self._get_price_overview(app_data)
        if price_dict:
            self.currency = price_dict['currency']
            self.initial_price = price_dict['initial']
            self.final_price = price_dict['final']
            self.discount = self._calculate_discount(self.initial_price, 
                                                     self.final_price)
        else:
            self.currency = None
            self.initial_price = None
            self.final_price = None
            self.discount = 0

    def _calculate_discount(self, initial, current):
        """
        Calculates the % difference between initial and current price.

        Note: when initial is 0 (that is, old price was lower than the new one -
        very unlikely in Steam), we assume that increase is (new price * 100)%.
        """

        if current == 0:
            return -100

        difference = current - initial
        # Division by 0 is not allowed. 1, however, will not change the price.
        initial = 1 if initial == 0 else initial
        percent = (difference / initial) * 100

        return int(round(percent, 0))

    def _get_appid(self, json_data):
        """
        Finds app id in JSON data.

        :param json_data: data about a steam app in a dict format.
        :return: name of the app.
        """

        try:
            appid = json_data['steam_appid']
        except KeyError:
            appid = None
        return appid

    def _get_title(self, json_data):
        """
        Finds name in JSON data.

        :param json_data: data about a steam app in a dict format.
        :return: name of the app.
        """

        try:
            title = json_data['name']
        except KeyError:
            title = None
        return title

    def _get_release_date(self, json_data):
        """
        Finds release date of an app.

        :param json_data: data about a steam app in a dict format.
        :return: release date of the app.
        """

        try:
            date = json_data['release_date']['date']
        except KeyError:
            date = None
        return date

    def _get_metascore(self, json_data):
        """
        Finds metascore in JSON data.

        :param json_data: data about a steam app in a dict format.
        :return: metascore of the app.
        """

        try:
            meta = json_data['metacritic']['score']
        except KeyError:
            meta = None
        return meta

    def _get_description(self, json_data):
        """
        Finds description of an app in JSON data.

        :param json_data: data about a steam app in a dict format.
        :return: description of the app.
        """

        try:
            desc = json_data['short_description']
        except KeyError:
            desc = None
        return desc

    def _get_price_overview(self, json_data):
        """
        Finds information related to app price.

        :return: a dictionary of relevant price data.
        """

        try:
            price = json_data['price_overview']
        except KeyError:
            price = None
        return price

    @staticmethod
    def _fetch_text(origin):
        """
        Gets the textual JSON representation from a given link.

        :param origin: link to a resource.
        """

        try:
            response = requests.get(origin)
            response.raise_for_status()
        except requests.HTTPError:
            raise requests.HTTPError("Resource not found")
        else:
            return response.text

    def _get_app_data(self, json_text, title=None, appid=None, region=None):
        """
        Extracts dict in which app resides from JSON response by loading textual
        representation of JSON and applying private inner function to it over
        and over again.

        :params json_text: textual representation of JSON object.
        :return: dictionary that has the relevant information about an app.
        """

        app_dicts = []

        def _decode_dictionary(dictionary):
            """
            Search for key with "name" value that == target application name.
            If found, it means the dictionary is the one we are interested in.

            Typical input: {"appid": int, "name": str}
            """

            try:
                if title:
                    if dictionary["name"].lower() == title.lower():
                        app_dicts.append(dictionary)
                else:
                    if dictionary["appid"] == appid:
                        app_dicts.append(dictionary)
            except KeyError:
                pass
            return dictionary

        json.loads(json_text, object_hook=_decode_dictionary)
        json_data = self._choose_complete_json(app_dicts, region=region)

        return json_data

    @staticmethod
    def _choose_complete_json(dicts, region=None):
        """
        Goes through dictionaries to an app that can be consumed successfully.
        That is, sometimes in Steam app list apps have identical names.
        However, inputting corresponding ids to
            http://store.steampowered.com/api/appdetails?appids=id
        does not give any information back. E.g., there are 3 dictionaries
        that have their title as "Borderlands", with corresponding IDs as
        8950, 8980 and 8989. However, only 8980 responds to queries. All
        others return {"[appid]":{"success":false}}, which is not useful.
        Unfortunately, it is impossible to know which one will return a
        useful response (at least without resorting to 3rd party APIs).
        Hence, in worst case, each and every one of dicts will have to be
        checked, potentially slowing the application significantly.

        :param dicts: app dicts to be checked. Typical input:
                      {"appid": int, "name": str}
        :param region: region for which the information should be retrieved.
        :return: JSON of successful query (i.e., dictionary with app info)
        """

        if dicts:
            config = Config('steamCLI', 'resources.ini')
            base_url = config.get_value('SteamAPIs', 'appinfo')
            if not region:
                region = config.get_value('SteamRegions', 'default')
            for d in dicts:
                appid = d['appid']
                resource = f'{base_url}{appid}&cc={region}'
                response = requests.get(resource)
                data = response.json()
                if data[str(appid)]['success']:
                    return data[str(appid)]['data']
        return None
