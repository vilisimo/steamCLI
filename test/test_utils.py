# To run single test module:
# >>> python -m unittest test.test_some_module

import unittest

from unittest import mock

from steamCLI.utils import sanitize_title


class SanitizeTitlesTests(unittest.TestCase):
    def test_utf8_title(self):
        """
        Ensure that titles containing UTF-8 characters are transformed to 
        titles that have only ascii characters.
        """

        title = "special®char#another"
        expected = 'specialcharanother'
        actual = sanitize_title(title)

        self.assertEqual(expected, actual)

    def test_lowercase_letters(self):
        """ Ensure string is transformed to lowercase letters. """

        title = 'LOWErCASE'
        expected = 'lowercase'
        actual = sanitize_title(title)

        self.assertEqual(expected, actual)

    def test_converts_arabic_to_roman(self):
        """
        Ensure that arabic numerals are converted to roman ones. But in really 
        stupid fashion, as in 10 is not X, but I0...
        """

        title = '131'
        expected = 'iiiii'
        actual = sanitize_title(title)

        self.assertEqual(expected, actual)

    def test_convers_arabic_to_roman_2(self):
        """ Try different options. """

        title = 'rocketleague 2015'
        expected = 'rocketleagueii0iv'
        actual = sanitize_title(title)

        self.assertEqual(expected, actual)





