import argparse

def main():
    parser = argparse.ArgumentParser(description="A command line application to retrieve information on Steam games.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--title", action="store", metavar="",
                        help="title of a game or an app on Steam")
    group.add_argument("-id", "--appID", type=int, action="store", metavar="",
                        help="id of a game or an app on Steam")
    args = parser.parse_args()
    if args.title:
        print(args.title)
    if args.appID:
        print(args.appID * 2)


if __name__ == '__main__':
    main()