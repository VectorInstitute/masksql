"""Graph visualization utilities for SQL AST."""

import graphviz

from src.taxonomy.parse.node import SqlAstNode
from src.taxonomy.parse.visitor.tree_extractor import AstDiagramTreeExtractor


def draw_graph(ast: SqlAstNode, out_path: str):
    """Draw and save a visual representation of the SQL AST.

    Parameters
    ----------
    ast : SqlAstNode
        The SQL AST root node to visualize.
    out_path : str
        Output file path (without extension) for the generated PNG.
    """
    visitor = AstDiagramTreeExtractor()
    root = ast.accept(visitor)
    graph = graphviz.Digraph(comment=ast.__class__.__name__)
    root.add_to_graph(graph)
    graph.render(out_path, format="png", cleanup=True)
