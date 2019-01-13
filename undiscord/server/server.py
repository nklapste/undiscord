# -*- coding: utf-8 -*-

"""flask/cheroot server definition"""

import os
from logging import getLogger
from uuid import uuid4

from flask import Flask, render_template, send_from_directory
from flask_restplus import Resource, Api, reqparse, fields

from undiscord.bot.__main__ import scrape_server, DEFAULT_MESSAGES_NUMBER, \
    DEFAULT_TIMEOUT
from undiscord.friend_map import FriendMap, PlotlyAdapter
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
connections_parser.add_argument('token', type=str, help='User Discord token')
connections_parser.add_argument('server_name', type=str,
                                help="Name of the Discord server to collect "
                                     "messages from")
connections_parser.add_argument('messages_number', type=int,
                                default=DEFAULT_MESSAGES_NUMBER,
                                help="Number of Discord messages to collect")
connections_parser.add_argument('timeout', type=float,
                                default=DEFAULT_TIMEOUT,
                                help="Time to collect Discord messages before "
                                     "stopping")

connections_model = API.schema_model('Connections', {
    "type": "array",
    "items": {
        "type": "array",
        "minItems": 2,
        "maxItems": 2,
        "items": {
            "type": "string"
        }
    }
})


@API.route('/api/connections')
@API.expect(connections_parser)
class GetConnections(Resource):
    @API.marshal_with(connections_model, code=201, description='Object created')
    def post(self):
        args = connections_parser.parse_args()
        server_data = scrape_server(
            token=args['token'],
            server_name=args["server_name"],
            messages_number=args["messages_number"],
            timeout=args["timeout"]
        )
        connections = list(get_connections_from_server(server_data))
        return connections, 201


graph_url_model = API.model('graphURL', {"graphURL": fields.String})


@API.route('/api/graph')
@API.expect(connections_parser)
class GetConnectionsGraph(Resource):
    @API.marshal_with(graph_url_model, code=201, description='Object created')
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
