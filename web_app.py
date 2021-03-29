# this file is just a wrapper for the `web` module
from argparse import ArgumentParser

from web.server import run_server

if __name__ == "__main__":
    parser = ArgumentParser(description='Fyp system webserver')
    parser.add_argument('--port', '-p', type=int, action='store', default=5000, help='port number (default = 5000)')

    args = parser.parse_args()

    run_server(args.port)
