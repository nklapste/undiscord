# -*- coding: utf-8 -*-

"""Generate a network graph from connection data"""

from json import load

import matplotlib.pyplot as plt
import networkx as nx
import plotly
import plotly.graph_objs as go
from plotly.offline.offline import _plot_html

from undiscord.reply_pry import get_connections_from_server


def spectral_layout(G):
    return nx.spectral_layout(G, scale=0.01)


def reingold(G):
    return nx.fruchterman_reingold_layout(G, k=0.25)


layouts: dict = {
    "reingold": reingold,
    "spectral": spectral_layout,  # TODO: not working
    "random": nx.random_layout
}


class FriendMap:
    """Takes a json file from ___and created a directed graph"""

    def __init__(self, server_data: dict):
        self.graph = nx.DiGraph()
        self.graph_title = server_data['name'] + " Network graph"
        self.add_nodes(server_data)
        self.add_connections(server_data)

    def add_connections(self, data):
        for orig_author, reply_author in get_connections_from_server(data):
            if self.graph.has_edge(orig_author, reply_author):
                self.graph[orig_author][reply_author]['weight'] += 1
            else:
                self.graph.add_edge(orig_author, reply_author, weight=1)

    def plot(self, filename: str):
        nx.spring_layout(self.graph)
        nx.draw_networkx(self.graph)
        plt.axis('off')
        plt.title(self.graph_title)
        plt.savefig(filename, format="PNG")
        plt.show(block=False)

    def get_title(self):
        return self.graph_title

    def get_graph(self):
        return self.graph

    def add_nodes(self, server_data):
        for channel in server_data["channels"]:
            for message in channel["messages"]:
                self.graph.add_node(message["author"]["name"])


class PlotlyAdapter:
    """Takes a FriendMap and creates a plotly map from it"""

    def __init__(self, map: FriendMap, layout: str):
        self.title = map.get_title()
        self.edge_trace = []
        self.node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='Rainbow',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2)
            )
        )

        positions = layouts[layout](map.get_graph())
        self.set_nodes(map.get_graph(), positions)
        self.set_edges(map.get_graph(), positions)
        self.set_node_attributes(map.get_graph())

    def set_nodes(self, graph: nx.Graph, positions):
        for node in graph.nodes():
            x, y = positions[node]
            self.node_trace['x'] += tuple([x])
            self.node_trace['y'] += tuple([y])

    def set_edges(self, graph: nx.Graph, positions):
        for edge in graph.edges():
            x0, y0 = positions[edge[0]]
            x1, y1 = positions[edge[1]]
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=2, color=self.get_line_color(graph[edge[0]][edge[1]]['weight'])),
                hoverinfo='none',
                mode='lines')
            self.edge_trace.append(edge_trace)

    def set_node_attributes(self, graph: nx.Graph):
        for node, adjacencies in enumerate(graph.adjacency()):
            self.node_trace['marker']['color'] += tuple([len(adjacencies[1])])

        for node, adjacencies in enumerate(graph.adjacency()):
            node_info = adjacencies[0] + "<br>"
            node_info += 'Connections (' + str(len(adjacencies[1])) + "):<br>"
            for adj in adjacencies[1]:
                node_info += "   " + adj + "<br> "
            self.node_trace['text'] += tuple([node_info])

    def plot_graph(self, filename: str):
        plotly.offline.plot(self.get_figure(), filename=filename, auto_open=False)
        pass

    def get_html(self):
        return "<html><head>  <script src='https://cdn.plot.ly/plotly-latest.min.js'></script></head><body>" \
               + plotly.offline.plot(self.get_figure(), include_plotlyjs=False, output_type='div') + "</body></html>"

    def get_figure(self):
        return go.Figure(
            data=[*self.edge_trace, self.node_trace],
            layout=go.Layout(
                title=self.title,
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )

    @staticmethod
    def get_line_color(weight: int) -> str:
        if weight == 1:
            return '#ff0000'
        elif weight == 2:
            return '#ffbf00'
        elif weight <= 5:
            return '#80ff00'
        elif weight < 10:
            return '#00ff40'
        elif weight < 20:
            return '#00ffff'
        elif weight < 25:
            return '#0040ff'
        else:
            return '#8000ff'


if __name__ == "__main__":
    with open("discord-ding-ding_messages.json") as data:
        friend_map = FriendMap(load(data))
    html_graph = PlotlyAdapter(friend_map, "reingold")
    html_graph.plot_graph("reingold.html")
    print(html_graph.get_html())
