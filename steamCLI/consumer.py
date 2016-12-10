""" Responsible for consuming various Steam APIs """

import requests
import json

from requests.exceptions import HTTPError


APP_LIST_API = 'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'


class Resource:
    def __init__(self, root=APP_LIST_API):
        """
        :params root: API root address.
        """

        self.root = root
        self.dest = None

    def __str__(self):
        return self.root if not self.dest else self.dest

    def get_destination(self, *args):
        """ Constructs resource's destination. """

        if args:
            self.dest = self.root + "/".join(args)
        else:
            self.dest = self.root

    def fetch_json(self):
        """
        Consumes a resource to get JSON response. 

        NOTE: at the moment, stores as object's attribute. Could be wasteful?
        """

        if not self.dest:
            self.get_destination()

        try:
            response = requests.get(self.dest)
            response.raise_for_status()
        except HTTPError:
            raise HTTPError("Resource not found.")
        else:
            self.json = response.json()

    def fetch_text(self):
        """
        Returns a text representation of json. So that the search can be 
        performed via json loads. Should not be used for anything else but 
        app list.
        """

        if not self.dest:
            self.get_destination()

        try:
            response = requests.get(self.dest)
            response.raise_for_status()
        except HTTPError:
            raise HTTPError("Resource not found")
        else:
            return response.text


class SteamApp:
    def __init__(self, title=None, appID=None):
        self.title = title
        self.id = appID

    def get_app_dict(self, json_text, target_app):
        """ 
        Extracts dict in which app resides from JSON response by loading textual
        representation of JSON and applying private inner function to it over and 
        over again. 

        :params json_text: textual representation of JSON object.
        :params target_app: string representation of target steam app.
        """

        app_dict = []

        def _decode_dictionary(dictionary):
            """
            Search for key with "name" value that equals target application name. If
            found, it means the dictionary is the one we are interested in.
            """
            try:
                if dictionary["name"] == target_app:
                    app_dict.append(dictionary)
            except KeyError:
                pass
            return dictionary

        json.loads(json_text, object_hook=_decode_dictionary)

        return app_dict[0] if app_dict else None






