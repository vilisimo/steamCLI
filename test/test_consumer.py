import os
import sys
import unittest

from unittest import mock

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

from requests.exceptions import HTTPError
from steamCLI.consumer import (
    Resource,
    SteamApp,
)


# Test URL
URL = 'http://api.example.com/test/'
STEAM_MOCK = '{"applist": {"apps": {"app": [{"appid": 5,"name": "Dedicated Server"}]}}}'


def mocked_requests_get(*args):


    class MockedResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.text = STEAM_MOCK

        def json(self):
            return self.json_data

        def raise_for_status(self):
            return "OK"

    if args[0] == URL:
        return MockedResponse(STEAM_MOCK, 200)
    else:
        raise HTTPError()


class TestResource(unittest.TestCase):
    def setUp(self):
        url = 'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'
        self.resource = Resource(root=url)

    def test_str(self):
        """ Ensures str representation shows the resource's dest. """
        expected = 'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'

        self.assertEqual(expected, str(self.resource))

    def test_dest_construction(self):
        """ Ensures resource's dest. is constructed properly. """

        resource = Resource(root=URL)
        params = ['test', 'this', 'resource']
        resource.get_destination(params[0], params[1], params[2])
        dest = resource.dest
        expected = URL + "/".join(params)

        self.assertEqual(expected, dest)

    def test_dest_construction_no_args(self):
        """ Destination should be the same as root with no arguments. """

        self.resource.get_destination()

        self.assertEqual(self.resource.root, self.resource.dest)

    @mock.patch('steamCLI.consumer.requests.get', side_effect=mocked_requests_get)
    def test_fetch_json_no_resource(self, mock_get):
        """ Ensures exception is raised if an destination is not correct. """

        with self.assertRaises(HTTPError):
            resource = Resource(URL)
            resource.get_destination('test')
            resource.fetch_text()

    @mock.patch('steamCLI.consumer.requests.get', side_effect=mocked_requests_get)
    def test_fetch_json_resource_exists(self, mock_get):
        """ Ensures correct json is returned when a resource can be accessed """

        resource = Resource(root=URL)
        resource.fetch_json()
        
        self.assertEqual(STEAM_MOCK, resource.json)

    @mock.patch('steamCLI.consumer.requests.get', side_effect=mocked_requests_get)
    def test_fetch_text_no_resource(self, mock_get):
        """ Ensures exception is raised if an destination is not correct. """

        with self.assertRaises(HTTPError):
            resource = Resource(URL)
            resource.get_destination('test')
            resource.fetch_text()

    @mock.patch('steamCLI.consumer.requests.get', side_effect=mocked_requests_get)
    def test_fetch_text(self, mock_get):
        """ Ensures a text representation of json is returned. """
        
        resource = Resource(root=URL)
        text_json = resource.fetch_text()

        self.assertEqual(STEAM_MOCK, text_json)


class TestSteamApp(unittest.TestCase):
    def setUp(self):
        self.steamapp = SteamApp()
        self.resource = Resource(root=URL)

    @mock.patch('steamCLI.consumer.requests.get', side_effect=mocked_requests_get)
    def test_get_app_dict(self, mock_get):
        """ Ensures get_app_dict() manages to find relevant dictionaries """

        text = self.resource.fetch_text()
        expected = {"appid": 5, "name": "Dedicated Server"}
        result = self.steamapp.get_app_dict(text, "Dedicated Server")

        self.assertEqual(expected, result)

    @mock.patch('steamCLI.consumer.requests.get', side_effect=mocked_requests_get)
    def test_get_app_dict_no_such_app(self, mock_get):
        """ Ensures that when nothing is found, None is returned. """

        text = self.resource.fetch_text()
        result = self.steamapp.get_app_dict(text, "Test")

        self.assertFalse(result)