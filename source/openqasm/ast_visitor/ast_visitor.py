from typing import Optional, TypeVar, Generic

from openqasm.ast import OpenNode

T = TypeVar("T")


class NodeVisitor(Generic[T]):
    """
    A node visitor base class that walks the abstract syntax tree and calls a
    visitor function for every node found.  This function may return a value
    which is forwarded by the `visit` method.

    Modified from the implementation in ast.py in the Python standard library.
    We added the context argument to the visit method. It allows the visitor
    to hold temporary state while visiting the nodes.

    The visit/generic_visit methods in subclasses do not have to have context argument.
    """

    def visit(self, node: OpenNode, context: Optional[T] = None):
        """Visit a node."""
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        # The visitor method may not have the context argument.
        if context:
            return visitor(node, context)
        else:
            return visitor(node)

    def generic_visit(self, node: OpenNode, context: Optional[T] = None):
        """Called if no explicit visitor function exists for a node."""
        for value in node.__dict__.values():
            if not isinstance(value, list):
                value = [value]
            for item in value:
                if isinstance(item, OpenNode):
                    if context:
                        self.visit(item, context)
                    else:
                        self.visit(item)


class NodeTransformer(NodeVisitor[T]):
    """
    A :class:`NodeVisitor` subclass that walks the abstract syntax tree and
    allows modification of nodes.

    Modified from the implementation in ast.py in the Python standard library
    """

    def generic_visit(self, node: OpenNode, context: Optional[T] = None) -> OpenNode:
        for field, old_value in node.__dict__.items():
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, OpenNode):
                        value = self.visit(value, context) if context else self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, OpenNode):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, OpenNode):
                new_node = self.visit(old_value, context) if context else self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node
