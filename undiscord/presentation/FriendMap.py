import networkx as nx
from json import load
import matplotlib.pyplot as plt


class FriendMap:

    def __init__(self, data_file_name: str):
        self.graph = nx.DiGraph()
        with open(data_file_name, 'r') as file:
            connections = load(file)

        self.graph_title = connections['name'] + " Network graph"

        for channel in connections["channels"]:
            for message in channel['messages']:
                self.add_connections(message)
        pass

    def add_connections(self, message: dict):
        author = message['author']['name']
        if not message['mentions']:
            self.graph.add_node(author)

        for mention in message['mentions']:
            self.graph.add_edge(author, mention['name'])
        pass

    def plot(self, filename: str):
        nx.spring_layout(self.graph)
        nx.draw_networkx(self.graph)
        plt.axis('off')
        plt.title(self.graph_title)
        plt.show()
        plt.savefig(filename, format="PNG")


map = FriendMap("data.json")
map.plot("test.png")
