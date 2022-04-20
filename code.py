from typing import Iterator, Literal
from graphviz import Digraph


Kind = Literal['tree', 'backward', 'forward', 'cross']

color: dict[Kind, str] = {
    'tree': 'black',
    'backward': 'blue',
    'forward': 'green',
    'cross': 'red',
}

class Graph(Digraph):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.label: dict[str, str] = {}
        self.nodes: dict[str, list[str]] = {}
        self.links: dict[tuple[str, str], Kind | None] = {}

    def node(self, name: str, label: str, *, is_root: bool = False):
        if is_root:
            super().node(name, f'{label}({name})', color='darkgray', style='filled')
        else:
            super().node(name, f'{label}({name})')
        self.label[name] = label
        self.nodes[name] = []

    def edge(self, tail: str, head: str, kind: Kind | None = None):
        self.nodes[tail].append(head)
        self.links[tail, head] = kind
        super().edge(tail, head, color=color.get(kind, 'darkgray'))

    def by_label(self, label: str) -> str | None:
        for node, name in self.label.items():
            if name == label:
                return node

    def render(self, name: str):
        super().render(name, quiet=True, quiet_view=True, view=True)


def lines(filename: str) -> Iterator[str]:
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip()


def read(nodes: str = 'nodes.csv', links: str = 'links.csv') -> Graph:
    graph = Graph('MO412')

    for line in lines(nodes):
        name, value, _, _ = line.split(',')
        graph.node(value, label=name)

    for line in lines(links):
        tail, head, _ = line.split(',')
        graph.edge(tail, head)

    return graph


def count(start: int = 0) -> Iterator[int]:
    while True:
        yield start
        start += 1


def dfs(graph: Graph, initial: str) -> tuple[dict[str, int], dict[str, int], dict[tuple[str, str], Kind]]:
    assert initial in graph.nodes

    start: dict[str, int] = {}
    end: dict[str, int] = {}
    edges: dict[tuple[str, str], Kind] = {}

    time = count()

    def dfs_visit(node: str, parent: str | None = None):
        if node in start:
            if not parent:
                return
            if node not in end:
                edges[parent, node] = 'forward'
            elif end[node] < start[parent]:
                edges[parent, node] = 'cross'
            else:
                edges[parent, node] = 'backward'
            return

        start[node] = next(time)
        for adj in graph.nodes[node]:
            dfs_visit(adj, parent=node)
        end[node] = next(time)

        if parent:
            edges[parent, node] = 'tree'

    dfs_visit(initial)
    for node in graph.nodes:
        dfs_visit(node)

    return start, end, edges


def colored_graph(graph: Graph, kind: dict[tuple[str, str], Kind], *, start: str | None = None) -> Graph:
    colored = Graph(graph.name or "Colored")

    for node in graph.nodes:
        colored.node(node, graph.label[node], is_root=(node == start))

    for tail, head in graph.links:
        colored.edge(tail, head, kind.get((tail, head)))

    return colored


if __name__ == "__main__":
    graph = read()
    start, end, edges = dfs(graph, graph.by_label('Ti'))

    graph = colored_graph(graph, edges, start=graph.by_label('Ti'))
    graph.render('out/graph.gv')

    for pair in graph.links:
        graph.links[pair] = edges.get(pair)

    with open('out/nodes.csv', 'w') as nodes:
        for node in graph.nodes:
            print(graph.label[node], node, start[node], end[node], sep=',', file=nodes)

    with open('out/links.csv', 'w') as links:
        for (tail, head), kind in graph.links.items():
            print(tail, head, kind, sep=',', file=links)
