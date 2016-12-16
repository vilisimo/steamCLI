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

# WHY IS ROOT USED? IS THERE A NEED FOR DEFAULT? I DON'T THINK SO


class Resource:
    def __init__(self, root=None):
        """
        :params root: API root address.
        """

        self.root = root
        self.origin = None
        self.json = None

    def __str__(self):
        return self.root if not self.origin else self.origin

    def construct_origin(self, *args):
        """ Constructs resource's origin. """

        if args:
            self.origin = self.root + "/".join(args)
        else:
            self.origin = self.root

    def fetch_json(self):
        """
        Consumes a resource to get JSON response. 

        NOTE: at the moment, stores as object's attribute. Could be wasteful?
        """

        if not self.origin:
            self.construct_origin()

        try:
            response = requests.get(self.origin)
            response.raise_for_status()
        except HTTPError:
            raise HTTPError("Resource not found.")
        else:
            self.json = response.json()
