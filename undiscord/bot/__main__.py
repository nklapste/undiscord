#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""argparse and entry point script for undiscord discord bot"""

import argparse
import sys
from logging import getLogger

from undiscord.common import add_log_parser, init_logging

__log__ = getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    """Create and return the argparser for undiscord discord bot"""
    parser = argparse.ArgumentParser(
        description="Start undiscord discord bot"
    )

    add_log_parser(parser)

    return parser


def main(argv=sys.argv[1:]) -> int:
    """main entry point undiscord discord bot"""
    parser = get_parser()
    args = parser.parse_args(argv)
    init_logging(args, "undiscord_bot.log")

    return 0


if __name__ == "__main__":
    sys.exit(main())
