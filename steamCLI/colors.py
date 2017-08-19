FAIL = '\033[91m'
END = '\033[0m'


def error(message):
    print(f"{FAIL}\nERROR!\n\n{message}{END}")
