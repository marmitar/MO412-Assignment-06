from __future__ import annotations
from math import inf
from typing import Iterator, TypeVar
from graphviz import Digraph


def lines(filename: str) -> Iterator[str]:
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip()


class Graph(Digraph):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.label: dict[str, str] = {}
        self.nodes: dict[str, list[str]] = {}

    def node(self, name: str, label: str, *, is_root: bool = False):
        if is_root:
            super().node(name, f'{label}({name})', color='darkgray', style='filled')
        else:
            super().node(name, f'{label}({name})')
        self.label[name] = label
        self.nodes[name] = []

    def edge(self, tail: str, head: str):
        self.nodes[tail].append(head)
        self.nodes[head].append(tail)

    def mark(self, tail: str, head: str):
        super().edge(tail, head)

    def by_label(self, label: str) -> str | None:
        for node, name in self.label.items():
            if name == label:
                return node

    def render(self, name: str):
        super().render(name, quiet=True, quiet_view=True, view=True)

    @staticmethod
    def read(nodes: str = 'nodes.csv', links: str = 'links.csv', root: str | None = None) -> Graph:
        graph = Graph('MO412')

        for line in lines(nodes):
            name, value, _, _ = line.split(',')
            graph.node(value, label=name, is_root=(name == root))

        for line in lines(links):
            tail, head = line.split(',')
            graph.edge(tail, head)

        return graph


class Queue(dict[str, tuple[str, int]]):
    def pop(self, key: str) -> tuple[str, int]:
        value = self[key]
        del self[key]
        return value

    def popmin(self) -> tuple[str, tuple[str, int]]:
        key, _ = min(self.items(), key=lambda pair: pair[1][1])
        return key, self.pop(key)

    def empty(self) -> bool:
        return len(self) <= 0

    def update(self, key: str, parent: str, distance: int) -> None:
        _, prev_dist = self.get(key, (None, inf))
        if distance < prev_dist:
            self[key] = (parent, distance)


def bfs(graph: Graph, initial: str) -> tuple[dict[str, int], dict[str, str]]:
    assert initial in graph.nodes

    dist: dict[str, int] = {initial: 0}
    parent: dict[str, str] = {}

    queue = Queue({adj: (initial, 1) for adj in graph.nodes[initial]})
    while not queue.empty():
        node, (prev, distance) = queue.popmin()
        graph.mark(prev, node)
        parent[node], dist[node] = prev, distance

        for adj in graph.nodes[node]:
            if adj not in dist:
                queue.update(adj, node, distance + 1)

    return dist, parent


if __name__ == "__main__":
    graph = Graph.read()
    dist, parent = bfs(graph, graph.by_label('Ti'))
    graph.render('out/graph.gv')

    with open('turnin/nodes.csv', 'w') as nodes:
        for node in graph.nodes:
            print(graph.label[node], node, parent.get(node), dist.get(node, inf), sep=',', file=nodes)

    with open('turnin/links.csv', 'w') as links:
        with open('links.csv', 'r') as original:
            for line in original:
                links.write(line)
