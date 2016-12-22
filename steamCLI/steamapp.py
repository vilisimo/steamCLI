import requests
import json


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
