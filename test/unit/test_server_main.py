# -*- coding: utf-8 -*-

import argparse

from undiscord.server.__main__ import get_parser, main


def test_get_parser():
    assert isinstance(get_parser(), argparse.ArgumentParser)


def test_smoke_main():
    assert main([]) == 0
