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

ALLOWED = set('abcdefghijklmnopqrstuvwxy0123456789')


def sanitize_title(title: str) -> str:
    """
    Sanitizes input so that it doesn't can be submitted to Is There Any Deal:
        1) digits need to be converted to their roman numeral counterparts
        2) 'the' needs to be removed
        3) special characters need to be removed

    Note: for strings such as 'Астролорды: Оружие Пришельцев' it does not
    work, because ITAD encodes them in really strange fashion... Common
    libraries do not work as required, and there is no documentation of
    encoding to help development of a custom tool.

    :param title: app's title which needs to be sanitized
    :return: sanitized string
    """

    lowercase_title = title.lower()
    articless = remove_articles(lowercase_title)
    sanitized = ''.join(filter(ALLOWED.__contains__, articless))
    numerals = list(sanitized)

    for index, key in enumerate(numerals):
        if key in TRANSFORMATIONS:
            numerals[index] = TRANSFORMATIONS[key]
    romanized = ''.join(numerals)

    return romanized


def remove_articles(text: str) -> str:
    """
    Removes articles from a given text. Not particularly fast, but since
    we are dealing with titles, no need to prematurely optimize.

    Note: currently, ITAD removes only 'the'...

    :param text: string from which articles (currently only 'the') need to be
                 removed
    :return: formatted string
    """

    articles = {'the': ''}
    remaining = []
    for word in text.split():
        if word not in articles:
            remaining.append(word)

    return ' '.join(remaining)


def calculate_discount(initial: int, current: int) -> int:
    """
    Calculates the % difference between initial and current price.

    Note: when initial is 0 (that is, old price was lower than the new one -
    very unlikely in Steam), we assume that increase is (new price * 100)%.

    :param initial: initial price
    :param current: current price
    :return integer: representing the discount
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
