#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""argparse and entry point script for undiscord flask/cheroot server"""

import argparse
import sys
from logging import getLogger

from undiscord.common import add_log_parser, init_logging

from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher

from undiscord.server.server import APP

__log__ = getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    """Create and return the argparser for undiscord flask/cheroot server"""
    parser = argparse.ArgumentParser(
        description="Start undiscord flask/cheroot server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    group = parser.add_argument_group("server")
    group.add_argument("-d", "--host", default='0.0.0.0',
                       help="hostname to listen on")
    group.add_argument("-p", "--port", default=8080, type=int,
                       help="port of the webserver")

    add_log_parser(parser)

    return parser


def main(argv=sys.argv[1:]) -> int:
    """main entry point undiscord flask/cheroot server"""
    parser = get_parser()
    args = parser.parse_args(argv)
    init_logging(args, "undiscord_server.log")

    d = PathInfoDispatcher({'/': APP})
    server = WSGIServer((args.host, args.port), d)

    try:
        __log__.info("starting server: host: {} port: {}".format(args.host, args.port))
        server.start()
    except KeyboardInterrupt:
        __log__.info("KeyboardInterrupt detected shutting down server")
        server.stop()
        return 0
    except Exception:
        __log__.exception("unexpected shutdown of undiscord server")
        raise


if __name__ == "__main__":
    sys.exit(main())
