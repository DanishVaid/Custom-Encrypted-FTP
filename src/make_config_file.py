#!/usr/local/bin/python3

import sys
import json
import argparse

def valid_option(args):
    if args.client is False and args.server is False:
        return False
    elif args.client is True and args.server is True:
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description='Simulate effect of network delay on audio files.')
    parser.add_argument('-c', "--client", help='Create a client config.', default=False, action="store_true")
    parser.add_argument('-s', "--server", help='Create a server config.', default=False, action="store_true")
    parser.add_argument('-f', "--file", type=str, help='Output config file name (No extension). Defaults to: myconfig.conf.json', default='myconfig.conf.json')
    args = parser.parse_args()


    if not valid_option(args):
        print("Invalid run option.")
        parser.print_help()
        sys.exit(0)

    output_file_path = args.file
    if output_file_path != 'myconfig.conf.json':
        output_file_path = output_file_path.split('.')[0] + '.conf.json'


    config = {}
    if args.client:
        config['client_ip']     = input("IP of client: ")
        config['client_port']   = input("Port to run client at: ")
        config['server_ip']     = input("IP of server: ")
        config['server_port']   = input("Port of server: ")
        config['server_public_key_path'] = input("Enter relative path to server's public key")
        print("Config for client set...")
    else:
        config['incoming_ip']     = input("IP of server: ")
        config['incoming_port']   = input("Port to run server at: ")
        config['outgoing_ip']     = input("IP of client: ")
        config['outgoing_port']   = input("Port of client: ")
        config['private_key_path'] = input("Enter relative path to server's private key") 
        print("Config for server set...")
    
    with open(output_file_path, 'w') as out_file:
            json.dump(config, out_file)

    print("Config file created:", output_file_path)

if __name__ == "__main__":
    main()