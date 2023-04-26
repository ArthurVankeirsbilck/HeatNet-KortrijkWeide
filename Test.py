from pyomo.environ import *
import math
import random
random.seed(10)
hours=1
randomlist = []
randomlist2 = []
randomlist3 = []
#Aanpassen nummers, numerical instability due to big
for i in range(0,hours):
    n = random.randint(1300,1301)
    randomlist.append(n)

for i in range(0,hours):
    n = random.randint(500,501)
    randomlist2.append(n)

for i in range(0,hours):
    n = random.randint(600,601)
    randomlist3.append(n)


node1_demands = randomlist
node2_demands = randomlist2
node3_demands = randomlist3
node1_costs = [1.8]*hours
node2_costs = [1.4]*hours
node3_costs = [1.0]*hours
Plants = ['Plant1', 'Plant2', 'Plant3']
def demands():
    demands_dict = {}
    #nodes
    for i in range(1, 4):
        #time periods
        for t in range(0, len(node1_demands)+1):
            # add demand to dictionary with node and time period as keys
            demands_dict[(i, t)] = eval(f"node{i}_demands[t-1]")
    return demands_dict

def gencosts():
    dict = {}
    # loop over nodes
    for i in range(1, 4):
        # loop over plants
        for t in range(0, len(node1_demands)+1):
            for p in Plants:
            # loop over time periods
                # add demand to dictionary with node, plant, and time period as keys
                dict[(i, p, t)] = eval(f"node{i}_costs[t-1]")
    return dict
print(gencosts())
T = len(node1_demands)+1
times = list(range(T))
# create model object
model = ConcreteModel()
# sets
model.T = Set(initialize=times)
model.I = Set(initialize=[1, 2, 3])  # set of nodes
model.J = Set(initialize=[1, 2, 3])  # set of nodes
model.Plants = Set(initialize=Plants)

# parameters
model.c = Param(model.I, model.J, initialize={
    (1, 2): 50, (1, 3): 50, (2, 1): 50, (2, 3): 50, (3, 1): 50, (3, 2): 50,
    (1, 1): 0, (2, 2): 0, (3, 3): 0  # initialize diagonal elements to zero
})  # transmission cost from i to j
model.p_max_plant = Param(model.I, model.Plants, initialize={
    (1, 'Plant1'): 1000, (1, 'Plant2'): 500, (1, 'Plant3'): 500,
    (2, 'Plant1'): 500, (2, 'Plant2'): 500, (2, 'Plant3'): 500,
    (3, 'Plant1'): 500, (3, 'Plant2'): 500, (3, 'Plant3'): 500
})

model.CHP_Plants = Set(within=model.I * model.Plants, initialize={
    (1, 'Plant1'), (1, 'Plant3'),
    (2, 'Plant1'), 
    (3, 'Plant1'), (3, 'Plant3')
    # (1, 'Plant1')
})

model.HOB_Plants = Set(within=model.I * model.Plants, initialize={
    (1, 'Plant2'), (2, 'Plant2'), (2, 'Plant3'), (3, 'Plant2')
})

M=8000
Cp=4.18
P_elec = 0.4 #Wordt aangeleverd door Jurgen
# massflow = 2.4

model.u = Param(model.I, model.J, initialize={(1, 2): M, (1, 3): M, (2, 1): M, (2, 3): M, (3, 1): M, (3, 2): M, (1, 1): 0, (2, 2): 0, (3, 3): 0})  # transmission capacity limit from i to j
model.d = Param(model.I, model.T, initialize=demands())  # net supply (supply - demand) in node i
model.c_gen = Param(model.I, model.Plants, model.T, initialize=gencosts())

model.k = Param(model.I, model.J, initialize={(1, 2): 0.3, (1, 3): 0.2, (2, 1): 0.3, (2, 3): 0.3, (3, 1): 0.2, (3, 2): 0.3,(1, 1): 0, (2, 2): 0, (3, 3): 0})
model.L = Param(model.I, model.J, initialize={(1, 2): 30, (1, 3): 20, (2, 1): 30, (2, 3): 30, (3, 1): 20, (3, 2): 30,(1, 1): 0, (2, 2): 0, (3, 3): 0})
model.Do = Param(model.I, model.J, initialize={(1, 2): 0.4, (1, 3): 0.3, (2, 1): 0.4, (2, 3): 0.4, (3, 1): 0.3, (3, 2): 0.4,(1, 1): 0.4, (2, 2): 0.4, (3, 3): 0.4})
model.Di = Param(model.I, model.J, initialize={(1, 2): 0.3, (1, 3): 0.2, (2, 1): 0.3, (2, 3): 0.3, (3, 1): 0.2, (3, 2): 0.3,(1, 1): 0.1, (2, 2): 0.1, (3, 3): 0.1})
model.cons = ConstraintList()
# variables
model.x = Var(model.I, model.J, model.T, bounds=(0, None))  # power transmission from i to j
model.p = Var(model.Plants, model.I, model.T, bounds=(0, None))  # production at node i
model.mean_c = Var()  # mean transmission cost
model.CQl = Var(model.I, model.J, model.T, bounds=(0, None))
model.Ql = Var(model.I, model.J, model.T, bounds=(0, None))
model.z = Var(model.I, model.J, model.T, domain=Binary)
model.Ts = Var(model.I, model.J, model.T, bounds=(60, 120))
model.Tr = Var(model.I, model.J, model.T, bounds=(30, 120))
model.y = Var(model.I, model.T, domain=Binary)
model.massflow = Var(model.I, model.J, model.T, bounds=(0, None))
model.P_el = Var(model.Plants, model.I, model.T, bounds=(0, None))
model.kappa = Var(model.I, model.Plants, model.T, domain=Binary)
M = 10000000
epsilon = 0.0000001

# objective
model.obj = Objective(
    expr=sum(model.c[i,j]*model.x[i,j,t] for j in model.J for i in model.I for t in model.T) + sum(model.c_gen[i,p,t]*model.p[p,i,t] for p in model.Plants for i in model.I for t in model.T), sense=minimize)

def balance_constraint_rule(model, i,j,t):
    return sum(model.x[i, j, t] - model.x[j, i, t] for j in model.J) + sum(model.p[p,i,t] for p in model.Plants) == model.d[i,t]

model.balance_constraint = Constraint(model.I, model.J, model.T , rule=balance_constraint_rule)

def heat_flow_constraint(model, i, j,t):
    return Cp*model.massflow[i,j,t]*(model.Ts[i,j,t]-model.Tr[i,j,t]) == model.d[i,t]

model.heat_flow_constraint = Constraint(model.I, model.J, model.T, rule=heat_flow_constraint)

def capacity_constraint_rule(model, i, j,t):
    return model.x[i, j,t] <= model.u[i, j]*model.z[i,j,t]

model.capacity_constraint = Constraint(model.I, model.J, model.T, rule=capacity_constraint_rule)

def production_constraint_rule(model, i, p ,t):
    return model.p[p,i,t] <= model.p_max_plant[i,p]

model.production_constraint = Constraint(model.I, model.Plants, model.T, rule=production_constraint_rule)

# def heatloss_constraint(model, i, j):
#     return model.Ql[i,j] == (((2.0*3.14*model.k[i,j]*model.L[i,j]*(model.Ts[i,j]-model.Tr[i,j]))/math.log(model.Do[i,j]/model.Di[i,j]))/1000)*model.z[i,j]
# model.heatloss_constraint = Constraint(model.I, model.J, rule=heatloss_constraint)


# def heatlosscost_constraint_rule(model, i, j):
#     return model.CQl[i,j] == model.Ql[i,j]*(
#         sum(model.p[p,i]*model.c_gen[i,p] for p in model.Plants) /
#         (sum(model.p[p,i] for p in model.Plants) + M * (1 - model.y[i]))
#     )

# model.heatlosscost_constraint = Constraint(model.I, model.J, rule=heatlosscost_constraint_rule)

# def sum_power_generation_rule(model, i):
#     return sum(model.p[p,i] for p in model.Plants) <= M* model.y[i]

# model.sum_power_generation_constraint = Constraint(model.I, rule=sum_power_generation_rule)

# def sum_power_generation_rule_2(model, i):
#     return sum(model.p[p,i] for p in model.Plants) >= epsilon * model.y[i]

# model.sum_power_generation_constraint_2 = Constraint(model.I, rule=sum_power_generation_rule_2)
# solve the model
solver = SolverFactory("octeract");
results = solver.solve(model, tee=True)

print(f"Objective value: {model.obj():.2f}")
for i in model.I:
    for j in model.J:
        if model.x[i, j]() > 0:
            print(f"From node {j} to node {i}: {model.x[i, j]():.2f} MWh")
print("Production:")
for i in model.I:
    for p in model.Plants:
        if model.p[p,i]() > 0:
            print(f"At node {i} at pp {p}: {model.p[p,i]():.2f} MWh")

print("Generation costs:")
for i in model.I:
    for p in model.Plants:
        if model.p[p,i].value > 0:
            print(f"At node {i} at pp {p}: {model.p[p,i].value*model.c_gen[i,p]:.2f} $")

print("Transmission costs:")
for i in model.I:
    for j in model.J:
        if model.x[i, j]() > 0:
            print(f"From node {j} to node {i}: {model.x[i, j].value*model.c[i, j]:.2f} $")

print("Temps:")
for i in model.I:
    for j in model.J:
        if i == j:
            pass
        else:
            if model.Tr[i,j].value > 0:
                print("Supply-Return temp {} -> {}: {} <-> {}°C".format(j,i,model   

# print("Massflows:")
# for i in model.I:
#     for j in model.J:
#         print("From node {} to node {}: {}".format(j,i,model.massflow[i,j].value))