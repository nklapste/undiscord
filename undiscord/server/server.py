# -*- coding: utf-8 -*-

# TODO: fill in server after other components complete
"""flask/cheroot server definition"""

from logging import getLogger

from flask import Flask

__log__ = getLogger(__name__)

APP = Flask(__name__)


@APP.route("/")
def hello():
    __log__.info("request received")
    return "Hello World!"
