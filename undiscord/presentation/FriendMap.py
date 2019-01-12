import networkx as nx
from json import load
import matplotlib.pyplot as plt

from undiscord.reply_pry import get_possible_connections_from_server


class FriendMap:

    def __init__(self, server_data: dict):
        self.graph = nx.DiGraph()
        self.graph_title = server_data['name'] + " Network graph"

        for channel in server_data["channels"]:
            for message in channel['messages']:
                self.add_connections_from_mentions(message)
        self.add_reply_connections(server_data)

    def add_reply_connections(self, data):
        for message, reply in get_possible_connections_from_server(data):
            if self.graph.has_edge(message["author"]["name"], reply["author"]["name"]):
                self.graph[message["author"]["name"]][reply["author"]["name"]]['weight'] += 1
            else:
                self.graph.add_edge(message["author"]["name"], reply["author"]["name"], weight=1)

    def add_connections_from_mentions(self, message: dict):
        author = message['author']['name']
        if not message['mentions']:
            self.graph.add_node(author)

        for mention in message['mentions']:
            if self.graph.has_edge(author, mention['name']):
                self.graph[author][mention['name']]['weight'] += 1
            else:
                self.graph.add_edge(author, mention['name'], weight=1)
        pass

    def plot(self, filename: str):
        nx.spring_layout(self.graph)
        nx.draw_networkx(self.graph)
        plt.axis('off')
        plt.title(self.graph_title)
        plt.show(block=False)
        plt.savefig(filename, format="svg")


if __name__ == "__main__":
    map = FriendMap(load("discord-ding-ding_messages.json"))
    map.plot("test.svg")
