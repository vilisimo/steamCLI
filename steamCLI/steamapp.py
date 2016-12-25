import requests
import json

from steamCLI.config import Config


class SteamApp:
    def __init__(self, title=None, appid=None):
        self.title = title
        self.appid = appid

    def assign_id(self, origin):
        """
        Assigns an app id to an app.

        :param origin: url to resource: where a list of games is located.
        """

        # If app already has a defined ID, there is no need to search for it.
        if self.appid:
            return

        text = self._fetch_text(origin)
        app_info = self._get_app_dict(text)

        self.appid = app_info['appid'] if app_info else None

    def assign_json_info(self):
        """ Retrieves and assigns information about an app to the object. """

        # Get JSON from a link specified in .ini file.
        config = Config('steamCLI', 'resources.ini')
        # NOTE: region should also be added to the end, like so: &cc=region
        resource = config.get_value('SteamAPIs', 'appinfo') + str(self.appid)
        app_data = self._fetch_json(resource)

        # Field assignment
        self.title = self._get_title(app_data)
        self.release_date = self._get_release_date(app_data)
        self.description = self._get_description(app_data)
        self.metacritic = self._get_metacritic_score(app_data)

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

    def _fetch_json(self, origin):
        """
        Extracts a JSON object from a given app link.

        :param origin: link to a resource that is to be consumed.
        """

        response = requests.get(origin)
        json_data = response.json()

        # Steam informs us whether the game was found or not.
        if not json_data[str(self.appid)]['success']:
            raise requests.HTTPError("Resource not found")

        return json_data

    def _get_title(self, json_data):
        """
        Finds name in JSON data.

        :param json_data: data about a steam app in a dict format.
        :return: name of the app.
        """

        try:
            title = json_data[str(self.appid)]['data']['name']
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
            date = json_data[str(self.appid)]['data']['release_date']['date']
        except KeyError:
            date = None
        return date

    def _get_metacritic_score(self, json_data):
        """
        Finds metacritic score in JSON data.

        :param json_data: data about a steam app in a dict format.
        :return: metacritic score of the app.
        """

        try:
            meta = json_data[str(self.appid)]['data']['metacritic']['score']
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
            desc = json_data[str(self.appid)]['data']['short_description']
        except KeyError:
            desc = None
        return desc

    def _get_price_overview(self, json_data):
        """
        Finds information related to app price.

        :return: a dictionary of relevant price data.
        """

        try:
            price = json_data[str(self.appid)]['data']['price_overview']
        except KeyError:
            price = None
        return price

    def _fetch_text(self, origin):
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

    def _get_app_dict(self, json_text):
        """
        Extracts dict in which app resides from JSON response by loading textual
        representation of JSON and applying private inner function to it over
        and over again.

        :params json_text: textual representation of JSON object.
        """

        app_dict = []

        def _decode_dictionary(dictionary):
            """
            Search for key with "name" value that == target application name.
            If found, it means the dictionary is the one we are interested in.
            """

            try:
                if dictionary["name"].lower() == self.title.lower():
                    # Can't do "d=None <..> d = dictionary": None is returned?..
                    app_dict.append(dictionary)
            except KeyError:
                pass
            return dictionary

        json.loads(json_text, object_hook=_decode_dictionary)

        return app_dict[0] if app_dict else None
