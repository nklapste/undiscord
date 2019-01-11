#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""argparse and entry point script for undiscord django server"""

import argparse
import sys
from logging import getLogger

from undiscord.common import add_log_parser, init_logging

__log__ = getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    """Create and return the argparser for undiscord django server"""
    parser = argparse.ArgumentParser(
        description="Start undiscord django server"
    )

    add_log_parser(parser)

    return parser


def main(argv=sys.argv[1:]) -> int:
    """main entry point undiscord django server"""
    parser = get_parser()
    args = parser.parse_args(argv)
    init_logging(args, "undiscord_server.log")

    return 0


if __name__ == "__main__":
    sys.exit(main())
