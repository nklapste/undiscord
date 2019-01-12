# -*- coding: utf-8 -*-

# TODO: fill in server after other components complete
"""flask/cheroot server definition"""

from logging import getLogger

from flask import Flask
from flask_restplus import Resource, Api, reqparse

from undiscord.bot.__main__ import scrape_server
from undiscord.presentation.FriendMap import FriendMap, PlotlyAdapter
from undiscord.reply_pry import get_connections_from_server

__log__ = getLogger(__name__)

APP = Flask(__name__)

API = Api(
    APP, version='1.0', title='undiscord API',
    description='A simple API to obtain discord member correlation data'
)

connections_parser = reqparse.RequestParser()
connections_parser.add_argument('token', type=str, help='user discord token')
connections_parser.add_argument('messages_number', type=int, default=10)
connections_parser.add_argument('timeout', type=float, default=30.0)
connections_parser.add_argument('server_name', type=str)


@API.route('/api/connections')
@API.expect(connections_parser)
class GetConnections(Resource):
    def post(self):
        # parse request arguments
        args = connections_parser.parse_args()
        token = args['token']
        messages_number = args["messages_number"]
        timeout = args["timeout"]
        server_name = args["server_name"]
        server_data = scrape_server(token, server_name, messages_number,
                                    timeout)
        connections = list(get_connections_from_server(server_data))
        return connections, 201


@API.route('/api/graph')
@API.expect(connections_parser)
class GetGraph(Resource):
    def post(self):
        # parse request arguments
        args = connections_parser.parse_args()
        token = args['token']
        messages_number = args["messages_number"]
        timeout = args["timeout"]
        server_name = args["server_name"]
        server_data = scrape_server(token, server_name, messages_number,
                                    timeout)
        friend_map = FriendMap(server_data)
        html_graph = PlotlyAdapter(friend_map, "reingold")
        html_graph.plot_graph("mock-data.html")
        with open("mock-data.html") as graph_html:
            graph_html_text = graph_html.read()
        return graph_html_text, 201
