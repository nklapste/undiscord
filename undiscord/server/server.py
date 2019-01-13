# -*- coding: utf-8 -*-

"""flask/cheroot server definition"""

import os
from logging import getLogger
from uuid import uuid4

from flask import Flask, render_template, send_from_directory
from flask_restplus import Resource, Api, reqparse

from undiscord.bot.__main__ import scrape_server, DEFAULT_MESSAGES_NUMBER, \
    DEFAULT_TIMEOUT
from undiscord.presentation.FriendMap import FriendMap, PlotlyAdapter
from undiscord.reply_pry import get_connections_from_server

__log__ = getLogger(__name__)

APP = Flask(__name__)

GRAPH_DIR: str = "graph"


@APP.route('/', methods=["GET"])
def index():
    # parse request arguments
    return render_template('index.html')


@APP.route('/graph/<graph_uuid>', methods=["GET"])
def graph(graph_uuid):
    return send_from_directory(GRAPH_DIR, '{}.html'.format(graph_uuid))


API = Api(
    APP,
    version='1.0',
    title='undiscord API',
    doc='/api/doc',
    description='A simple API to obtain discord member correlation data'
)


connections_parser = reqparse.RequestParser()
connections_parser.add_argument('token', type=str, help='user discord token')
connections_parser.add_argument('messages_number', type=int,
                                default=DEFAULT_MESSAGES_NUMBER)
connections_parser.add_argument('timeout', type=float,
                                default=DEFAULT_TIMEOUT)
connections_parser.add_argument('server_name', type=str)


@API.route('/api/connections')
@API.expect(connections_parser)
class GetConnections(Resource):
    def post(self):
        args = connections_parser.parse_args()
        server_data = scrape_server(
            token=args['token'],
            server_name=args["server_name"],
            messages_number=args["messages_number"],
            timeout=args["timeout"]
        )
        connections = list(get_connections_from_server(server_data))
        return connections, 200


@API.route('/api/graph')
@API.expect(connections_parser)
class GetConnectionsGraph(Resource):
    def post(self):
        args = connections_parser.parse_args()
        server_data = scrape_server(
            token=args['token'],
            server_name=args['server_name'],
            messages_number=args['messages_number'],
            timeout=args["timeout"]
        )
        friend_map = FriendMap(server_data)
        html_graph = PlotlyAdapter(friend_map, "reingold")
        uuid = uuid4()
        os.makedirs(GRAPH_DIR, exist_ok=True)
        html_graph.plot_graph(os.path.join(GRAPH_DIR, "{}.html".format(uuid)))
        return {"graphURL": "/graph/{}".format(uuid)}, 201
