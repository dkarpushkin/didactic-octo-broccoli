import unittest

from phone_finder import search_in_html


class TestPhoneFinder(unittest.TestCase):

    def test_search_in_html(self):
        numbers = search_in_html(b'''<html>
        <body>
            <p>+7 999 999 99 99</p>
            <p>+7 (999) 999 99 99</p>
            <p>81234567890</p>
            <p>999 99 99</p>
            <p>12346</p>
        </body>
        </html>
        ''')

        assert(len(numbers) == 3)
        assert('+79999999999' in numbers)
        assert('+71234567890' in numbers)
        assert('+74959999999' in numbers)
