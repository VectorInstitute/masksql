"""Tree node implementation for diagram visualization of SQL AST."""

from typing import List, Optional

from graphviz import Digraph

from src.taxonomy.parse.visitor.visitor_result import MergeableVisitorResult


class DiagramTreeNode(MergeableVisitorResult):
    """A tree node for visualizing SQL AST structure as a diagram.

    Attributes
    ----------
    name : str
        The display name for this node.
    parent : Optional[DiagramTreeNode]
        The parent node in the tree.
    children : List[DiagramTreeNode]
        List of child nodes.
    shape : str
        The shape to use when rendering in graphviz.
    """

    name: str
    parent: Optional["DiagramTreeNode"]
    children: List["DiagramTreeNode"]
    shape: str

    def __init__(self, name: str, shape: str = "box"):
        self.name = name
        self.parent = None
        self.children = []
        self.shape = shape

    def merge(self, other):
        """Merge another node by adding it as a child."""
        return self.add_child(other)

    def add_child(self, child: "DiagramTreeNode"):
        """Add a child node to this node and set its parent reference."""
        if child is not None:
            child.parent = self
            self.children.append(child)
        return self

    def add_to_graph(self, graph: Digraph):
        """Recursively add this node and its children to the graph."""
        graph.node(self.id(), self.name, shape=self.shape)
        if self.parent:
            graph.edge(self.parent.id(), self.id())
        for child in self.children:
            child.add_to_graph(graph)

    def get_num_nodes(self) -> int:
        """Return the total number of nodes in this tree."""
        size = 1
        for c in self.children:
            size += c.get_num_nodes()
        return size

    def get_height(self) -> int:
        """Return the height of this tree."""
        if len(self.children) == 0:
            return 1
        return max([c.get_height() + 1 for c in self.children])

    def id(self):
        """Return the unique identifier for this node."""
        return str(id(self))
