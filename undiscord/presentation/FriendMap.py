# -*- coding: utf-8 -*-

"""Generate a network graph from connection data"""

from json import load

import matplotlib.pyplot as plt
import networkx as nx
import plotly
import plotly.graph_objs as go

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
        self.add_reply_connections(server_data)

    def add_reply_connections(self, data):
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


class PlotlyAdapter:
    """Takes a FriendMap and creates a plotly map from it"""

    def __init__(self, map: FriendMap, layout: str):
        self.title = map.get_title()
        self.edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
        self.node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
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
            self.edge_trace['x'] += tuple([x0, x1, None])
            self.edge_trace['y'] += tuple([y0, y1, None])

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
        fig = go.Figure(
            data=[self.edge_trace, self.node_trace],
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
        plotly.offline.plot(fig, filename=filename, auto_open=False)
        pass


if __name__ == "__main__":
    with open("discord-ding-ding_messages.json") as data:
        friend_map = FriendMap(load(data))
    html_graph = PlotlyAdapter(friend_map, "reingold")
    html_graph.plot_graph("reingold.html")
