import time
import math
from Pytrich.Heuristics.heuristic import Heuristic
from Pytrich.Search.htn_node import HTNNode
from Pytrich.model import Model, Operator, AbstractTask


class DeleteRelaxationHeuristic(Heuristic):
    """
    Delete-Relaxation Heuristic for HTN Planning

    Based on Hoeller et al. (2018): "Delete- and ordering-relaxation heuristics for HTN planning"
    """

    def __init__(self, use_ordering_relaxation=True, name="del_relax"):
        super().__init__(name=name)
        self.use_ordering_relaxation = use_ordering_relaxation
        self.relaxed_operators = {}
        self.task_costs = {}
        self.fact_costs = {}
        self.preprocessing_time = 0
        self.iterations = 0

    def initialize(self, model: Model, initial_node: HTNNode):
        start_time = time.time()

        self._create_relaxed_operators(model)
        self._compute_relaxed_costs(model, initial_node)
        self.preprocessing_time = time.time() - start_time

        initial_h = self._estimate_remaining_cost(initial_node.state, initial_node.task_network)
        self.update_info(initial_h)
        return initial_h

    def _create_relaxed_operators(self, model: Model):
        self.relaxed_operators = {}

        for op in model.operators:
            relaxed_op = type('RelaxedOperator', (), {
                'name': op.name,
                'global_id': op.global_id,
                'preconditions': getattr(op, 'pos_precons', 0),  # ? corrected
                'add_effects': getattr(op, 'add_effects', 0),
                'del_effects': 0,
                'cost': getattr(op, 'cost', 1)
            })()
            self.relaxed_operators[op.global_id] = relaxed_op

    def _compute_relaxed_costs(self, model: Model, initial_node: HTNNode):
        self.fact_costs = {
            i: (0 if initial_node.state & (1 << i) else math.inf)
            for i in range(len(model.facts))  # ? corrected
        }

        self.task_costs = {
            op.global_id: math.inf for op in model.operators
        }
        self.task_costs.update({
            task.global_id: math.inf for task in model.abstract_tasks
        })

        changed = True
        self.iterations = 0

        while changed:
            changed = False
            self.iterations += 1

            # Operator updates
            for op_id, op in self.relaxed_operators.items():
                old_cost = self.task_costs[op_id]
                preconds = op.preconditions or 0

                can_apply = True
                precond_cost = 0

                for i in range(preconds.bit_length()):
                    if preconds & (1 << i):
                        if self.fact_costs[i] == math.inf:
                            can_apply = False
                            break
                        precond_cost = max(precond_cost, self.fact_costs[i])

                if can_apply:
                    new_cost = precond_cost + op.cost
                    if new_cost < old_cost:
                        self.task_costs[op_id] = new_cost
                        changed = True

            # Abstract task decomposition updates
            for method in model.decompositions:  # ? corrected
                task_id = method.compound_task.global_id  # ? corrected
                old_cost = self.task_costs[task_id]

                if self.use_ordering_relaxation:
                    method_cost = max(
                        (self.task_costs.get(sub.global_id, math.inf)
                         for sub in method.task_network),
                        default=0
                    )
                else:
                    method_cost = sum(
                        self.task_costs.get(sub.global_id, math.inf)
                        for sub in method.task_network
                    )

                if method_cost < old_cost:
                    self.task_costs[task_id] = method_cost
                    changed = True

            # Fact updates
            for op_id, op in self.relaxed_operators.items():
                op_cost = self.task_costs[op_id]
                if op_cost < math.inf:
                    effects = op.add_effects or 0
                    for i in range(effects.bit_length()):
                        if effects & (1 << i):
                            if op_cost < self.fact_costs[i]:
                                self.fact_costs[i] = op_cost
                                changed = True

    def _estimate_remaining_cost(self, state, task_network):
        if not task_network:
            return 0

        if self.use_ordering_relaxation:
            return max(
                (self.task_costs.get(task.global_id, math.inf) for task in task_network),
                default=0
            )
        else:
            total = 0
            for task in task_network:
                cost = self.task_costs.get(task.global_id, math.inf)
                if cost == math.inf:
                    return 999999  # ? safe cap instead of math.inf
                total += cost
            return total

    def __call__(self, parent_node: HTNNode, node: HTNNode):
        h_value = self._estimate_remaining_cost(node.state, node.task_network)
        self.update_info(h_value)
        return h_value

    def __repr__(self):
        return f"DelRelax(ord_relax)" if self.use_ordering_relaxation else "DelRelax()"

    def __str__(self):
        return self.__repr__()

    def __output__(self):
        return (
            f"Heuristic info:\n"
            f"\tName: {self.name}\n"
            f"\tUse ordering relaxation: {self.use_ordering_relaxation}\n"
            f"\tRelaxed operators: {len(self.relaxed_operators)}\n"
            f"\tTask costs computed: {len(self.task_costs)}\n"
            f"\tFact costs computed: {len(self.fact_costs)}\n"
            f"\tIterations: {self.iterations}\n"
            f"\tPreprocessing time: {self.preprocessing_time:.2f} s\n"
        )
