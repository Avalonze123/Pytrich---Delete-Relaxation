import time
import math
from Pytrich.Heuristics.heuristic import Heuristic
from Pytrich.ProblemRepresentation.and_or_graph import AndOrGraph, ContentType, NodeType
from Pytrich.Search.htn_node import HTNNode
from Pytrich.model import Model


class HmaxHeuristic(Heuristic):
    """
    Hmax heuristic for HTN planning.
    This is based on the classical h_max heuristic, adapted for an HTN AND/OR graph.
    """

    def __init__(self, use_name="hmax_htn", name="hmax_htn"):
        super().__init__(name=name)
        self.h_values = {}
        self.and_or_graph = None
        self.preprocessing_time = 0
        self.iterations = 0

    def initialize(self, model: Model, initial_node: HTNNode):
        """
        Initialize the heuristic with the model and precompute hmax values.
        """
        start_time = time.time()

        # Build AND/OR graph for hmax computation
        self.and_or_graph = AndOrGraph(model, graph_type=4)

        # Compute hmax values for all nodes in the graph
        self._compute_hmax()

        # Store preprocessing time
        self.preprocessing_time = time.time() - start_time

        # Initial h-value for the root node
        initial_h = sum(self.h_values.get(t.global_id, math.inf) for t in initial_node.task_network)
        self.update_info(initial_h)
        return initial_h

    def _compute_hmax(self):
        """
        Propagate costs in the AND/OR graph using hmax combination:
        - OR node: min over predecessors
        - AND node: weight + max over predecessors
        """
        # Initialize node values
        for node in self.and_or_graph.nodes:
            if node is None:
                continue
            if node.type == NodeType.INIT:
                node.value = 0
            else:
                node.value = math.inf

        changed = True
        while changed:
            self.iterations += 1
            changed = False
            for node in self.and_or_graph.nodes:
                if node is None:
                    continue

                old_value = node.value
                if node.type == NodeType.OR:
                    if node.predecessors:
                        new_value = min(p.value for p in node.predecessors)
                    else:
                        new_value = node.value
                elif node.type == NodeType.AND:
                    if node.predecessors:
                        new_value = node.weight + max(p.value for p in node.predecessors)
                    else:
                        new_value = node.weight
                else:
                    new_value = node.value

                if new_value < old_value:
                    node.value = new_value
                    changed = True

        # Store values for operators, abstract tasks, and facts
        for n in self.and_or_graph.nodes:
            if n is None:
                continue
            if n.content_type in {ContentType.OPERATOR, ContentType.ABSTRACT_TASK, ContentType.FACT}:
                self.h_values[n.ID] = n.value

    def __call__(self, parent_node: HTNNode, node: HTNNode):
        """
        Return hmax value for the given node's remaining task network.
        """
        h_val = sum(self.h_values.get(t.global_id, math.inf) for t in node.task_network)
        self.update_info(h_val)
        return h_val

    def __repr__(self):
        return "HmaxHTN()"

    def __str__(self):
        return self.__repr__()

    def __output__(self):
        return (
            f"Heuristic info:\n"
            f"\tName: {self.name}\n"
            f"\tGraph size: {len(self.h_values)}\n"
            f"\tIterations: {self.iterations}\n"
            f"\tPreprocessing time: {self.preprocessing_time:.2f} s\n"
        )
