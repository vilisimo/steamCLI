TRANSFORMATIONS = {
    "1": 'i',
    "2": 'ii',
    "3": 'iii',
    "4": 'iv',
    "5": 'v',
    "6": 'vi',
    "7": 'vii',
    "8": 'viii',
    "9": 'ix',
}

WHITELIST = set('abcdefghijklmnopqrstuvwxy0123456789')


def sanitize_title(title):
    """
    Sanitizes input so that it doesn't can be submitted to Is There Any Deal.

    Note: for strings such as 'Астролорды: Оружие Пришельцев' it does not work, 
    because ITAD encodes them in really strange fashion...
    """

    # remove_utf = title.lower().encode('ascii', 'ignore').decode("UTF-8")
    # whitespaceless = remove_utf.replace(' ', '')
    sanitized = ''.join(filter(WHITELIST.__contains__, title.lower()))
    numerals = list(sanitized)

    for index, letter in enumerate(numerals):
        if letter in TRANSFORMATIONS:
            numerals[index] = TRANSFORMATIONS[letter]
    result = ''.join(numerals)

    return result


def calculate_discount(initial, current):
    """
    Calculates the % difference between initial and current price.

    Note: when initial is 0 (that is, old price was lower than the new one -
    very unlikely in Steam), we assume that increase is (new price * 100)%.
    """

    if initial is None or current is None:
        return 0

    if current == 0:
        return -100

    difference = current - initial
    # Division by 0 is not allowed. 1, however, will not change the price.
    initial = 1 if initial == 0 else initial
    percent = (difference / initial) * 100

    return int(round(percent, 0))