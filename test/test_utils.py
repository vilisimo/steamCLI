# To run single test module:
# >>> python -m unittest test.test_some_module

import unittest

from unittest import mock

from steamCLI.utils import sanitize_title, calculate_discount


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


class CalculateDiscountTests(unittest.TestCase):
    """ Test suite for functions that support SteamApp's functionality. """

    def test_calculate_discount_proper_values(self):
        """
        Ensures the function calculates correct percentage with valid values.
        """

        initial = 100.00
        current = 50.00
        expected = -50
        percent = calculate_discount(initial, current)

        self.assertEqual(expected, percent)

    def test_calculate_discount_doubles(self):
        """ Ensures correct percentages are derived from doubles. """

        initial = 29.99
        current = 7.49
        expected = -75
        percent = calculate_discount(initial, current)

        self.assertEqual(expected, percent)

    def test_calculate_price_higher_than_before(self):
        """ Ensure that initial < current does not break the function """

        initial = 1
        current = 3
        expected = 200
        percent = calculate_discount(initial, current)

        self.assertEqual(expected, percent)

    def test_calculate_price_zero(self):
        """ Ensure that zero initial/current does not break the function. """

        initial = 0
        current = 3
        expected = 300
        percent = calculate_discount(initial, current)

        self.assertEqual(expected, percent)

    def test_calculate_app_free(self):
        """ Ensure that when a game/app is free, discount is shown as -100%. """

        initial = 16456.46
        current = 0
        expected = -100
        percent = calculate_discount(initial, current)

        self.assertEqual(expected, percent)

    def test_calculate_price_is_none(self):
        """
        Ensure that when either of the prices is None, 0 is returned:
            - initial price = None -> x$ always has 0% discount from None
            - final price = None -> x$ is always 0% higher than None
        """

        initial = None
        current = 100
        expected = 0
        percent = calculate_discount(initial, current)

        self.assertEqual(expected, percent)

        initial = 100
        current = None
        expected = 0
        percent = calculate_discount(initial, current)

        self.assertEqual(expected, percent)


