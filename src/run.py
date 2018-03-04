#!/usr/local/bin/python3

import sys
import argparse

import server_pkg.server as server
import client_pkg.client as client

def valid_option(args):
    if args.client is False and args.server is False:
        return False
    elif args.client is True and args.client is True:
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description='Simulate effect of network delay on audio files.')
    parser.add_argument('-c', "--client", help='Run the client end.', default=False, action="store_true")
    parser.add_argument('-s', "--server", help='Run the server end.', default=False, action="store_true")
    parser.add_argument('-f', "--file", help='Config file to use.', default=None)
    args = parser.parse_args()

    if valid_option(args):
        if args.client:
            client.init(args.file)
        else:
            server.init(args.file)
    else:
        print("Invalid run option.")
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
	main()