""" Responsible for consuming various Steam-related APIs """

import configparser
import requests
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