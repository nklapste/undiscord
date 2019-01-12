# -*- coding: utf-8 -*-

import argparse

from undiscord.server.__main__ import get_parser


def test_get_parser():
    assert isinstance(get_parser(), argparse.ArgumentParser)
