# -*- coding: utf-8 -*-

import argparse

import pytest

from undiscord.bot.__main__ import get_parser, main


def test_get_parser():
    assert isinstance(get_parser(), argparse.ArgumentParser)


def test_smoke_main():
    with pytest.raises(SystemExit):
        main([])
