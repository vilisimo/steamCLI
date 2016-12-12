""" Responsible for consuming various Steam-related APIs """

import configparser
import requests
import json
import os

from requests.exceptions import HTTPError

# Read in relevant resource links.
current_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(current_dir, 'resources.ini')
config = configparser.ConfigParser()
config.read(config_file)
APP_LIST = config['SteamAPIs']['applist']


class Resource:
    def __init__(self, root=APP_LIST):
        """
        :params root: API root address.
        """

        self.root = root
        self.dest = None
        self.json = None

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


class SteamApp:
    # Static(-ish) variable. Only one resource location should ever be needed.
    apps = APP_LIST

    def __init__(self, title=None, app_id=None):
        self.title = title
        self.appID = app_id

    def fetch_text(self):
        """
        Returns a text representation of JSON. So that the search can be 
        performed via json.loads(). Should not be used for anything else but 
        app list - there's no need to use it elsewhere, really.
        """

        try:
            response = requests.get(SteamApp.apps)
            response.raise_for_status()
        except HTTPError:
            raise HTTPError("Resource not found")
        else:
            return response.text

    def get_app_dict(self, json_text):
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
                if dictionary["name"] == self.title:
                    # Can't do "d=None <..> d = dictionary": None is returned?..
                    app_dict.append(dictionary)
            except KeyError:
                pass
            return dictionary

        json.loads(json_text, object_hook=_decode_dictionary)

        return app_dict[0] if app_dict else None

    def assign_id(self):
        """ Extracts app's ID from the dictionary (see get_app_dict()). """

        text = self.fetch_text()
        app_info = self.get_app_dict(text)

        self.appID = app_info['appid'] if app_info else None

