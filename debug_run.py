from Pytrich.Grounder import ground_problem
from Pytrich.Search.htn_node import HTNNode

# Path to your HDDL domain and problem
domain_file = "/scratch/users/t02pa24/Project MSC/Pytrich/ipc2023-domains/total-order/AssemblyHierarchical/domain.hddl"
problem_file = "/scratch/users/t02pa24/Project MSC/Pytrich/ipc2023-domains/total-order/AssemblyHierarchical/genericLinearProblem_depth01.hddl"

# Ground the HDDL domain + problem
model = ground_problem(domain_file, problem_file)

# Create initial HTNNode (state)
initial_node = HTNNode(model)

# Print state representation (#10)
print("=== State Representation ===")
print(initial_node.task_network)

# Print static info (#11)
print("\n=== Static Information ===")
print(model.static_predicates)
from Pytrich.Grounder import ground_problem
from Pytrich.Search.htn_node import HTNNode

# Path to your HDDL domain and problem
domain_file = "/scratch/users/t02pa24/Project MSC/Pytrich/ipc2023-domains/total-order/AssemblyHierarchical/domain.hddl"
problem_file = "/scratch/users/t02pa24/Project MSC/Pytrich/ipc2023-domains/total-order/AssemblyHierarchical/genericLinearProblem_depth01.hddl"

# Ground the HDDL domain + problem
model = ground_problem(domain_file, problem_file)

# Create initial HTNNode (state)
initial_node = HTNNode(model)

# Print state representation (#10)
print("=== State Representation ===")
print(initial_node.task_network)

# Print static info (#11)
print("\n=== Static Information ===")
print(model.static_predicates)

