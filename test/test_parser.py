import unittest

from unittest import mock

from requests.exceptions import HTTPError
from steamCLI.parser import Resource

# To run single test module:
# >>> python -m unittest test.test_some_module

# Test URL & mock result
URL = 'http://api.example.com/test/'
STEAM_MOCK = '{"applist": {"apps": {"app": [{"appid": 8,"name": "winui2"}]}}}'


def mocked_get(*args):
    """ Function that mocks requests.get() """
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
        self.url = 'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'
        self.resource = Resource(root=self.url)

    def test_str(self):
        """ Ensures str representation shows the resource's origin """

        self.assertEqual(self.url, str(self.resource))

    def test_origin_construction(self):
        """ Ensures resource's origin is constructed properly. """

        resource = Resource(root=URL)
        params = ['test', 'this', 'resource']
        resource.construct_origin(params[0], params[1], params[2])
        origin = resource.origin
        expected = URL + "/".join(params)

        self.assertEqual(expected, origin)

    def test_origin_construction_no_args(self):
        """ Origin should be the same as root with no arguments. """

        self.resource.construct_origin()

        self.assertEqual(self.resource.root, self.resource.origin)

    @mock.patch('steamCLI.parser.requests.get')
    def test_fetch_json_no_resource(self, mock_get):
        """ Ensures exception is raised if an origin is not correct. """

        mock_get.side_effect = HTTPError()
        with self.assertRaises(HTTPError):
            resource = Resource(URL + 'test')
            resource.fetch_json()

        self.assertIn(mock.call(URL + 'test'), mock_get.call_args_list)

    @mock.patch('steamCLI.parser.requests.get', side_effect=mocked_get)
    def test_fetch_json_resource_exists(self, mock_get):
        """ Ensures correct json is returned when a resource can be accessed """

        resource = Resource(root=URL)
        resource.fetch_json()
        
        self.assertEqual(STEAM_MOCK, resource.json)
        self.assertIn(mock.call(URL), mock_get.call_args_list)