from pyomo.environ import *

def create_model(N, H_in, H_out, H_demand, H_max):
    model = ConcreteModel()

    # Sets
    model.N = Set(initialize=N)

    # Parameters
    model.H_in = Param(model.N, initialize=H_in)
    model.H_out = Param(model.N, initialize=H_out)
    model.H_demand = Param(model.N, initialize=H_demand)
    model.H_max = Param(initialize=H_max)

    # Decision Variables
    model.H_flow = Var(model.N, model.N, within=NonNegativeReals)
    model.H_utilized = Var(model.N, within=NonNegativeReals)
    model.H_excess = Var(model.N, within=NonNegativeReals)
    model.H_production = Var(model.N, within=NonNegativeReals)
    model.y = Var(model.N, model.N, within=Binary)

    # Objective
    model.obj = Objective(expr=sum(model.H_excess[i] for i in model.N))

    # Constraints
    def heat_balance_rule(model, i):
        if i == 1:
            return model.H_in[1] + sum(model.H_flow[j, 1] for j in model.N) == sum(model.H_flow[1, j] for j in model.N) + model.H_excess[1] - model.H_production[1]
        else:
            return sum(model.H_flow[i, j] for j in model.N) - sum(model.H_flow[j, i] for j in model.N) == model.H_utilized[i] + model.H_excess[i] - model.H_production[i]
    model.heat_balance_constraint = Constraint(model.N, rule=heat_balance_rule)

    def utilization_constraint_rule(model, i):
        return model.H_utilized[i] <= model.H_demand[i]
    model.utilization_constraint = Constraint(model.N, rule=utilization_constraint_rule)

    def maximum_flow_constraint_rule(model, j):
        return sum(model.H_flow[i, j] for i in model.N) <= model.H_max
    model.maximum_flow_constraint = Constraint(model.N, rule=maximum_flow_constraint_rule)

    def excess_constraint_rule(model, i, j):
        if i < j:
            return model.H_excess[i] == model.H_in[i] - model.H_utilized[i] - model.H_production[i]
        else:
            return model.H_excess[i] == model.H_in[i] - model.H_utilized[i] - model.H_production[i]
    model.excess_constraint = Constraint(model.N, model.N, rule=excess_constraint_rule)

    def utilization_extraction_rule(model, i, j):
        return model.H_utilized[i] <= model.H_in[i] * model.y[i, j]
    model.utilization_extraction_constraint = Constraint(model.N, model.N, rule=utilization_extraction_rule)

    return model

# Example usage
N = [1, 2, 3]  # Set of nodes
H_in = {1: 100, 2: 0, 3: 50}  # Heat input at each node
H_out = {1: 0, 2: 0, 3: 0}  # Heat output at each node
H_demand = {1: 80, 2: 60, 3: 70}  # Heat demand at each node
H_max = 200  # Maximum heat capacity of the pipe

model = create_model(N, H_in, H_out, H_demand, H_max)

# Solve the optimization model
solver = SolverFactory('glpk')  # Choose the solver (e.g., GLPK)
results = solver.solve(model)

# Print the results
if results.solver.termination_condition == TerminationCondition.optimal:
    model.display()
else:
    print("Solver did not converge to an optimal solution.")

