#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""argparse and entry point script for undiscord flask/cheroot server"""

import argparse
import os
import sys
from logging import getLogger

from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher

import undiscord.server.server
from undiscord.common import add_log_parser, init_logging

__log__ = getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    """Create and return the argparser for undiscord flask/cheroot server"""
    parser = argparse.ArgumentParser(
        description="Start the UnDiscord flask/cheroot server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    group = parser.add_argument_group("server")
    group.add_argument("-d", "--host", default='0.0.0.0',
                       help="Hostname to listen on")
    group.add_argument("-p", "--port", default=8080, type=int,
                       help="Port of the webserver")
    group.add_argument("-g", "--graph-dir", dest="graph_dir", default="graph",
                       help="Directory to store generated graphs")
    group.add_argument("--debug", action="store_true",
                       help="Run the server in Flask debug mode")
    add_log_parser(parser)

    return parser


def main(argv=sys.argv[1:]) -> int:
    """main entry point undiscord flask/cheroot server"""
    parser = get_parser()
    args = parser.parse_args(argv)
    init_logging(args, "undiscord_server.log")

    graph_dir = os.path.abspath(args.graph_dir)
    os.makedirs(graph_dir, exist_ok=True)

    __log__.info("starting server: host: {} port: {} graph_dir: {}".format(args.host, args.port, graph_dir))

    if args.debug:
        undiscord.server.server.GRAPH_DIR = graph_dir
        undiscord.server.server.APP.run(
            host=args.host,
            port=args.port,
            debug=True
        )
    else:
        path_info_dispatcher = PathInfoDispatcher({'/': undiscord.server.server.APP})
        server = WSGIServer((args.host, args.port), path_info_dispatcher)
        try:
            server.start()
        except KeyboardInterrupt:
            __log__.info("stopping server: KeyboardInterrupt detected")
            server.stop()
            return 0
        except Exception:
            __log__.exception("stopping server: unexpected exception")
            raise


if __name__ == "__main__":
    sys.exit(main())
