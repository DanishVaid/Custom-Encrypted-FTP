#!/usr/local/bin/python3

import sys
import argparse
import os

import server_pkg.server as server
import client_pkg.client as client

def valid_option(args):
    if args.client is False and args.server is False:
        return False
    elif args.client is True and args.server is True:
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description='Simulate effect of network delay on audio files.')
    parser.add_argument('-c', "--client", help='Run the client end.', default=False, action="store_true")
    parser.add_argument('-s', "--server", help='Run the server end.', default=False, action="store_true")
    parser.add_argument('-f', "--file", help='Config file to use.', default=None)
    args = parser.parse_args()


    if not valid_option(args):
        print("Invalid run option.")
        parser.print_help()
        sys.exit(0)

    if args.file is None:
        print("No config file specified, using default configuration.")
    elif os.path.isfile(args.file):
        print("ERROR: Config file not found.") 
        sys.exit(0)

    if args.client:
        client.init(args.file)
    else:
        server.init(args.file)
        


if __name__ == "__main__":
	main()