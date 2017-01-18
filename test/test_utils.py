# To run single test module:
# >>> python -m unittest test.test_some_module

import unittest

from steamCLI.utils import sanitize_title, calculate_discount, remove_articles


class SanitizeTitlesTests(unittest.TestCase):
    def test_should_remove_utf8_characters(self):
        """
        Ensure that titles containing UTF-8 characters are transformed to 
        titles that have only ascii characters.
        """

        expected_title = 'specialcharanother'
        actual_title = sanitize_title(title="special®char#another")

        self.assertEqual(expected_title, actual_title)

    def test_should_transform_title_to_lowercase(self):
        """ Ensure string is transformed to lowercase letters. """

        expected_title = 'lowercase'
        actual_title = sanitize_title(title='LOWErCASE')

        self.assertEqual(expected_title, actual_title)

    def test_should_convert_arabic_to_roman(self):
        """
        Ensure that arabic numerals are converted to roman ones. But in really 
        stupid fashion, as in 10 is not X, but I0...
        """

        expected_title = 'iiiii'
        actual_title = sanitize_title(title='131')

        self.assertEqual(expected_title, actual_title)

    def test_should_convert_arabic_to_roman_another(self):
        """ Try different options. """

        expected_title = 'rocketleagueii0iv'
        actual_title = sanitize_title(title='rocketleague 2015')

        self.assertEqual(expected_title, actual_title)


class RemoveArticlesTests(unittest.TestCase):
    """ Test suite to ensure that articles are properly removed from titles. """

    def test_should_not_remove_anything(self):
        """ Ensure that with no articles string is unchanged. """

        expected_text = 'text without articles or anything like that'
        actual_text = remove_articles(expected_text)

        self.assertEqual(expected_text, actual_text)

    def test_should_remove_the(self):
        """ Ensure that article 'the' is removed from the title. """

        changeable_text = 'the company'
        expected_text = changeable_text[4:]
        actual_text = remove_articles(changeable_text)

        self.assertEqual(expected_text, actual_text)

    def test_should_not_remove_the_in_the_middle_of_a_word(self):
        """ Ensure 'the' is not removed when it is part of a word. """

        expected_text = 'grand theft auto'
        actual_text = remove_articles(expected_text)

        self.assertEqual(expected_text, actual_text)


class CalculateDiscountTests(unittest.TestCase):
    """ Test suite for functions that support SteamApp's functionality. """

    def test_should_calculate_discount_with_proper_values(self):
        """
        Ensures the function calculates correct percentage with valid values.
        """

        percent = calculate_discount(initial=100.00, current=50.00)

        self.assertEqual(-50, percent)

    def test_should_calculate_discount_with_doubles(self):
        """ Ensures correct percentages are derived from doubles. """

        percent = calculate_discount(initial=29.99, current=7.49)

        self.assertEqual(-75, percent)

    def test_should_calculate_discount_when_price_is_higher_than_before(self):
        """ Ensure that initial < current does not break the function """

        percent = calculate_discount(initial=1, current=3)

        self.assertEqual(200, percent)

    def test_should_calculate_discount_when_initial_price_was_zero(self):
        """ Ensure that zero initial/current does not break the function. """

        percent = calculate_discount(initial=0, current=3)

        self.assertEqual(300, percent)

    def test_should_calculate_as_100_discount_when_app_is_free(self):
        """ Ensure that when a game/app is free, discount is shown as -100%. """

        percent = calculate_discount(initial=16456.46, current=0)

        self.assertEqual(-100, percent)

    def test_should_calculate_discount_as_0_when_price_is_none(self):
        """
        Ensure that when either of the prices is None, 0 is returned:
            - initial price = None -> x$ always has 0% discount from None
            - final price = None -> x$ is always 0% higher than None
        """

        percent = calculate_discount(initial=None, current=100)
        self.assertEqual(0, percent)

        percent = calculate_discount(initial=100, current=None)
        self.assertEqual(0, percent)
