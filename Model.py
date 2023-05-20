from pyomo.environ import *

# Create a ConcreteModel object
model = ConcreteModel()

# Sets
model.N = Set(initialize=[1, 2, 3, 4])
model.T = Set(initialize=[1, 2, 3])
model.PowerLines = Set(initialize=[1, 2])

# Parameters
model.P_gen = Param(model.N, model.T, initialize={
    (1, 1): 50, (1, 2): 60, (1, 3): 70,
    (2, 1): 80, (2, 2): 90, (2, 3): 100,
    (3, 1): 70, (3, 2): 80, (3, 3): 90,
    (4, 1): 70, (4, 2): 80, (4, 3): 90
})
model.P_import = Param(model.N, model.T, initialize={
    (1, 1): 30, (1, 2): 40, (1, 3): 50,
    (2, 1): 20, (2, 2): 30, (2, 3): 40,
    (3, 1): 10, (3, 2): 20, (3, 3): 30,
    (4, 1): 10, (4, 2): 20, (4, 3): 30
})
model.P_export = Param(model.N, model.T, initialize={
    (1, 1): 20, (1, 2): 30, (1, 3): 40,
    (2, 1): 10, (2, 2): 20, (2, 3): 30,
    (3, 1): 30, (3, 2): 40, (3, 3): 50,
    (4, 1): 30, (4, 2): 40, (4, 3): 50
})
model.C_gen = Param(model.N, model.T, initialize={
    (1, 1): 5, (1, 2): 6, (1, 3): 7,
    (2, 1): 4, (2, 2): 5, (2, 3): 6,
    (3, 1): 6, (3, 2): 7, (3, 3): 8,
    (4, 1): 6, (4, 2): 7, (4, 3): 8
})
model.C_import = Param(model.N, model.T, initialize={
    (1, 1): 8, (1, 2): 9, (1, 3): 10,
    (2, 1): 9, (2, 2): 10, (2, 3): 11,
    (3, 1): 7, (3, 2): 8, (3, 3): 9,
    (4, 1): 7, (4, 2): 8, (4, 3): 9
})
model.C_export = Param(model.N, model.T, initialize={
    (1, 1): 3, (1, 2): 4, (1, 3): 5,
    (2, 1): 2, (2, 2): 3, (2, 3): 4,
    (3, 1): 4, (3, 2): 5, (3, 3): 6,
    (4, 1): 4, (4, 2): 5, (4, 3): 6
})
model.P_transmission = Param(initialize=100)

model.Line = Param(model.N, within=model.PowerLines, initialize={
    1: 1,  # Prosumer 1 is assigned to power line 1
    2: 1,  # Prosumer 2 is also assigned to power line 1
    3: 2,   # Prosumer 3 is assigned to power line 2
    4:2
})
M = 1000

# Parameters
model.Demand = Param(model.N, model.T, initialize={     
    (1, 1): 20, (1, 2): 30, (1, 3): 40,
    (2, 1): 25, (2, 2): 35, (2, 3): 45,
    (3, 1): 30, (3, 2): 40, (3, 3): 50,
    (4, 1): 30, (4, 2): 40, (4, 3): 50
})

# Decision Variables
model.P = Var(model.N, model.T, within=NonNegativeReals)
model.I = Var(model.N, model.T, within=NonNegativeReals)
model.E = Var(model.N, model.T, within=NonNegativeReals)
model.M_flow = Var(model.PowerLines, model.T, bounds=(0, 40),within=NonNegativeReals)
model.T_supply = Var(model.PowerLines, model.T, bounds=(60, 120),within=NonNegativeReals)
model.T_return = Var(model.PowerLines, model.T, bounds=(30, 120),within=NonNegativeReals)
model.T_mixed = Var(model.PowerLines, model.T, bounds=(30, 120), within=NonNegativeReals)
model.T_incoming = Var(model.N, model.T, bounds=(30, 120), within=NonNegativeReals)
model.Q_loss = Var(model.PowerLines, model.T, within=NonNegativeReals)
model.X = Var(model.N, model.T, within=Binary)
model.Z = Var(model.N, model.N, within=Binary)

# Objective Function
def objective_rule(model):
    return sum(model.C_gen[i, t] * model.P[i, t] + model.C_import[i, t] * model.I[i, t] - model.C_export[i, t] * model.E[i, t]
               for i in model.N for t in model.T)
model.objective = Objective(rule=objective_rule, sense=minimize)

# Constraints
def demand_constraint_rule(model, i, t):
    return model.P[i, t] + model.I[i, t] >= model.Demand[i, t]
model.demand_constraint = Constraint(model.N, model.T, rule=demand_constraint_rule)

# Constraints
def generation_constraint_rule(model, i, t):
    return model.P[i, t] <= model.P_gen[i, t]
model.generation_constraint = Constraint(model.N, model.T, rule=generation_constraint_rule)

def import_constraint_rule(model, i, t):
    return model.I[i, t] <= model.P_import[i, t] * model.X[i, t]
model.import_constraint = Constraint(model.N, model.T, rule=import_constraint_rule)

def export_constraint_rule(model, i, t):
    return model.E[i, t] <= model.P_export[i, t]* model.X[i, t]
model.export_constraint = Constraint(model.N, model.T, rule=export_constraint_rule)

def transmission_constraint_rule(model, t):
    return sum(model.P[i, t] - model.E[i, t] + model.I[i, t] for i in model.N) <= model.P_transmission
model.transmission_constraint = Constraint(model.T, rule=transmission_constraint_rule)

# Constraint
def power_line_connection_constraint_rule(model, i, j):
    if i != j:
        return model.Z[i, j] <= (model.Line[i] == model.Line[j])
    else:
        return Constraint.Skip
model.power_line_connection_constraint = Constraint(model.N, model.N, rule=power_line_connection_constraint_rule)

# Additional constraint to ensure X is consistent with Z
def consistency_constraint_rule(model, i, t):
    return model.X[i, t] == sum(model.Z[i, j] for j in model.N if i != j)
model.consistency_constraint = Constraint(model.N, model.T, rule=consistency_constraint_rule)

# def energy_balance_constraint_rule(model, pipe, t):
#     return sum(model.P[i, t] * model.X[i, t] for i in model.N) == model.M_flow[pipe, t] * 4.1 * (model.T_mixed[pipe, t] - model.T_return[pipe, t])

def energy_balance_constraint_rule(model, pipe, t):
    return sum(model.P[i, t] * model.X[i, t] for i in model.N) + model.Q_loss[pipe, t] == model.M_flow[pipe, t] * 4.1 * (model.T_mixed[pipe, t] - model.T_return[pipe, t])
model.energy_balance_constraint = Constraint(model.PowerLines, model.T, rule=energy_balance_constraint_rule)


# model.energy_balance_constraint = Constraint(model.PowerLines, model.T, rule=energy_balance_constraint_rule)

def mixing_constraint_rule(model, i, t, pipe):
    return model.T_mixed[pipe, t] == (sum(model.M_flow[pipe, t] * 4.1 * model.T_supply[pipe, t]* model.X[i, t] for pipe in model.PowerLines) +
                                  model.M_flow[model.Line[i], t] * 4.1 * model.T_incoming[i, t])/(sum(model.M_flow[pipe, t] *4.1* model.X[i, t] for pipe in model.PowerLines) + model.M_flow[model.Line[i], t] * 4.1)

model.mixing_constraint = Constraint(model.N, model.T, model.PowerLines, rule=mixing_constraint_rule)

def heat_loss_constraint_rule(model, pipe, t):
    return model.Q_loss[pipe, t] == 0.05 * (model.T_supply[pipe, t] - 15)
model.heat_loss_constraint = Constraint(model.PowerLines, model.T, rule=heat_loss_constraint_rule)


solver = SolverFactory("octeract");
results = solver.solve(model,tee=True)

for t in model.T:
    for pipe in model.PowerLines:
        print(pipe, t, model.M_flow[pipe, t].value,model.T_supply[pipe, t].value, model.T_return[pipe, t].value)
        