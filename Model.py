from pyomo.environ import *

def CHP_feasible_area(yA):
    xA = 0
    xB = round(yA*(180/247))
    yB = round(yA*(215/247))
    xC = round(yA*(104.8/247))
    yC = round(yA*(81/247))
    xD = 0
    yD = round(yA*(81/247));

    return xA, xB, yB, xC, yC, xD, yD
nodes = [1, 2, 3, 4]
# Create a ConcreteModel object
model = ConcreteModel()
Plants = ['Plant1', 'Plant2', 'Plant3']
# Sets
model.N = Set(initialize=nodes)
model.T = Set(initialize=[1, 2, 3])
model.PowerLines = Set(initialize=[1, 2])
model.Plants = Set(initialize=Plants)

hours=500
node1_demands = [10]*hours
node2_demands = [20]*hours
node3_demands = [5]*hours
node4_demands = [30]*hours

Plants = ['Plant1', 'Plant2', 'Plant3']


def demands():
    demands_dict = {}
    #nodes
    for i in range(1, len(nodes)+1):
        #time periods
        for t in range(0, len(node1_demands)+1):
            # add demand to dictionary with node and time period as keys
            demands_dict[(i, t)] = eval(f"node{i}_demands[t-1]")
    return demands_dict
    
# Parameters
model.P_gen = Param(model.N, model.Plants, initialize={
    (1, 'Plant1'):50,(1, 'Plant2'):50,(1, 'Plant3'):50,
    (2, 'Plant1'):50,(2, 'Plant2'):50,(2, 'Plant3'):50,
    (3, 'Plant1'):50,(3, 'Plant2'):50,(3, 'Plant3'):50,
    (4, 'Plant1'):50,(4, 'Plant2'):50,(4, 'Plant3'):50,
})
CHP_plants ={
    (1, 'Plant1'),(4, 'Plant1')  
}
HOB_plants ={
    (1, 'Plant2'),(1, 'Plant3'),
    (2, 'Plant1'),(2, 'Plant2'),(2, 'Plant3'),
    (3, 'Plant1'),(3, 'Plant2'),(3, 'Plant3'),
    (4, 'Plant2'),(4, 'Plant3'),
}

model.CHP_Plants = Set(within=model.N * model.Plants, initialize=CHP_plants)
model.HOB_Plants = Set(within=model.N * model.Plants, initialize=HOB_plants)

model.P_import = Param(model.N, initialize={
    1:50,
    2:50,
    3:50,
    4:50
})
model.P_export = Param(model.N, initialize={
    1:50,
    2:50,
    3:50,
    4:50
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
model.P = Var(model.Plants,model.N, model.T, within=NonNegativeReals)
model.I = Var(model.N, model.T, within=NonNegativeReals)
model.E = Var(model.N, model.T, within=NonNegativeReals)
model.M_flow = Var(model.PowerLines, model.T, bounds=(0, 40),within=NonNegativeReals)
model.T_supply = Var(model.PowerLines, model.T, bounds=(60, 120),within=NonNegativeReals)
model.T_return = Var(model.PowerLines, model.T, bounds=(30, 120),within=NonNegativeReals)
model.X = Var(model.N, model.T, within=Binary)
model.Z = Var(model.N, model.N, within=Binary)
model.kappa= Var(model.N, model.Plants,model.T, within=Binary)
model.P_el = Var(model.Plants, model.N, model.T, bounds=(0, None))
M=10000

# Objective Function
def objective_rule(model):
    return sum(model.C_gen[i, t] * model.P[p, i, t] + model.C_import[i, t] * model.I[i, t] - model.C_export[i, t] * model.E[i, t] - 0.4*model.P_el[p,i,t]
               for i in model.N for t in model.T for p in model.Plants)
model.objective = Objective(rule=objective_rule, sense=minimize)

# Constraints
def demand_constraint_rule(model, i, t, p):
    return model.P[p, i, t] + model.I[i, t] >= model.Demand[i, t]
model.demand_constraint = Constraint(model.N, model.T, model.Plants, rule=demand_constraint_rule)

def import_constraint_rule(model, i, t):
    return model.I[i, t] <= model.P_import[i] * model.X[i, t]
model.import_constraint = Constraint(model.N, model.T, rule=import_constraint_rule)

def export_constraint_rule(model, i, t):
    return model.E[i, t] <= model.P_export[i]* model.X[i, t]
model.export_constraint = Constraint(model.N, model.T, rule=export_constraint_rule)

def transmission_constraint_rule(model, t):
    return sum(model.P[p, i, t]  - model.E[i, t] + model.I[i, t] for i in model.N for p in model.Plants) <= model.P_transmission
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

def energy_balance_constraint_rule(model, pipe, t):
    return sum(model.P[p, i, t] * model.X[i, t] for i in model.N for p in model.Plants) == model.M_flow[pipe, t] * (0.0007*model.T_supply[pipe, t]+4.1484) * (model.T_supply[pipe, t] - model.T_return[pipe, t])

model.energy_balance_constraint = Constraint(model.PowerLines, model.T, rule=energy_balance_constraint_rule)

def CHP_1(model, t, i, p):
    return model.P_el[p,i,t] - model.P_gen[i,p] - ((model.P_gen[i,p]-CHP_feasible_area(model.P_gen[i,p])[2])/(CHP_feasible_area(model.P_gen[i,p])[0]-CHP_feasible_area(model.P_gen[i,p])[1])) * (model.P[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[0]) <= 0
model.CHP_1_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_1)

def CHP_2(model, t, i, p):
    return model.P_el[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[2] - ((CHP_feasible_area(model.P_gen[i,p])[2]-CHP_feasible_area(model.P_gen[i,p])[4])/(CHP_feasible_area(model.P_gen[i,p])[1]-CHP_feasible_area(model.P_gen[i,p])[3])) * (model.P[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[1]) >= M*(model.kappa[i,p,t] - 1)
model.CHP_2_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_2)

def CHP_3(model, t, i, p):
    return model.P_el[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[4] - ((CHP_feasible_area(model.P_gen[i,p])[4]-CHP_feasible_area(model.P_gen[i,p])[6])/(CHP_feasible_area(model.P_gen[i,p])[3]-CHP_feasible_area(model.P_gen[i,p])[5])) * (model.P[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[3]) >= M*(model.kappa[i,p,t] - 1)
model.CHP_3_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_3)

def CHP_4(model, t, i, p):
    return CHP_feasible_area(model.P_gen[i,p])[6]*model.kappa[i,p,t] <= model.P_el[p,i,t]
model.CHP_4_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_4)

def CHP_5(model, t, i, p):
    return model.P_el[p,i,t] <= model.P_gen[i,p]*model.kappa[i,p,t]
model.CHP_5_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_5)

def CHP_6(model, t, i, p):
    return 0 <= model.P[p,i,t]
model.CHP_6_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_6)

def CHP_7(model, t, i, p):
    return model.P[p,i,t] <= CHP_feasible_area(model.P_gen[i,p])[1]*model.kappa[i,p,t]
model.CHP_7_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_7)

def HOB_1(model, t, i, p):
    return model.P_el[p,i,t]  ==  0
model.HOB_1_constraint = Constraint(model.T,model.HOB_Plants, rule=HOB_1)

def HOB_2(model, t, i, p):
    return model.P[p,i,t] <= model.P_gen[i,p]*model.kappa[i,p,t]
model.HOB_2_constraint = Constraint(model.T, model.HOB_Plants, rule=HOB_2)

solver = SolverFactory("octeract");
results = solver.solve(model,tee=True)

for t in model.T:
    for pipe in model.PowerLines:
        print(pipe, t, model.M_flow[pipe, t].value,model.T_supply[pipe, t].value, model.T_return[pipe, t].value)
        