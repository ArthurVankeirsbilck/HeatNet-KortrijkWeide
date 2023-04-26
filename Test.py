from pyomo.environ import *
import math
import random

def CHP_feasible_area(yA):
    xA = 0
    xB = round(yA*(180/247))
    yB = round(yA*(215/247))
    xC = round(yA*(104.8/247))
    yC = round(yA*(81/247))
    xD = 0
    yD = round(yA*(81/247));

    return xA, xB, yB, xC, yC, xD, yD

random.seed(10)
hours=1
randomlist = []
randomlist2 = []
randomlist3 = []
#Aanpassen nummers, numerical instability due to big
for i in range(0,hours):
    n = random.randint(900,1301)
    randomlist.append(n)

for i in range(0,hours):
    n = random.randint(300,501)
    randomlist2.append(n)

for i in range(0,hours):
    n = random.randint(2000,2601)
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
    expr=sum(model.c[i,j]*model.x[i,j,t] for j in model.J for i in model.I for t in model.T) + sum(model.c_gen[i,p,t]*model.p[p,i,t] - P_elec*model.P_el[p,i,t] for p in model.Plants for i in model.I for t in model.T), sense=minimize)

def balance_constraint_rule(model, i,j,t):
    return sum(model.x[i, j, t] - model.x[j, i, t] for j in model.J) + sum(model.p[p,i,t] for p in model.Plants) == model.d[i,t]

model.balance_constraint = Constraint(model.I, model.J, model.T , rule=balance_constraint_rule)

def heat_flow_constraint(model, i, j,t):
    return Cp*model.massflow[i,j,t]*(model.Ts[i,j,t]-model.Tr[i,j,t]) == model.d[i,t]

model.heat_flow_constraint = Constraint(model.I, model.J, model.T, rule=heat_flow_constraint)

def capacity_constraint_rule(model, i, j,t):
    return model.x[i, j,t] <= model.u[i, j]

model.capacity_constraint = Constraint(model.I, model.J, model.T, rule=capacity_constraint_rule)

def CHP_1(model, t, i, p):
    return model.P_el[p,i,t] - model.p_max_plant[i,p] - ((model.p_max_plant[i,p]-CHP_feasible_area(model.p_max_plant[i,p])[2])/(CHP_feasible_area(model.p_max_plant[i,p])[0]-CHP_feasible_area(model.p_max_plant[i,p])[1])) * (model.p[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[0]) <= 0
model.CHP_1_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_1)

def CHP_2(model, t, i, p):
    return model.P_el[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[2] - ((CHP_feasible_area(model.p_max_plant[i,p])[2]-CHP_feasible_area(model.p_max_plant[i,p])[4])/(CHP_feasible_area(model.p_max_plant[i,p])[1]-CHP_feasible_area(model.p_max_plant[i,p])[3])) * (model.p[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[1]) >= M*(model.kappa[i,p,t] - 1)
model.CHP_2_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_2)

def CHP_3(model, t, i, p):
    return model.P_el[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[4] - ((CHP_feasible_area(model.p_max_plant[i,p])[4]-CHP_feasible_area(model.p_max_plant[i,p])[6])/(CHP_feasible_area(model.p_max_plant[i,p])[3]-CHP_feasible_area(model.p_max_plant[i,p])[5])) * (model.p[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[3]) >= M*(model.kappa[i,p,t] - 1)
model.CHP_3_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_3)

def CHP_4(model, t, i, p):
    return CHP_feasible_area(model.p_max_plant[i,p])[6]*model.kappa[i,p,t] <= model.P_el[p,i,t]
model.CHP_4_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_4)

def CHP_5(model, t, i, p):
    return model.P_el[p,i,t] <= model.p_max_plant[i,p]*model.kappa[i,p,t]
model.CHP_5_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_5)

def CHP_6(model, t, i, p):
    return 0 <= model.p[p,i,t]
model.CHP_6_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_6)

def CHP_7(model, t, i, p):
    return model.p[p,i,t] <= CHP_feasible_area(model.p_max_plant[i,p])[1]*model.kappa[i,p,t]
model.CHP_7_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_7)

def HOB_1(model, t, i, p):
    return model.P_el[p,i,t]  ==  0
model.HOB_1_constraint = Constraint(model.T,model.HOB_Plants, rule=HOB_1)

def HOB_2(model, t, i, p):
    return model.p[p,i,t] <= model.p_max_plant[i,p]*model.kappa[i,p,t]
model.HOB_2_constraint = Constraint(model.T, model.HOB_Plants, rule=HOB_2)

def heatloss_constraint(model, i, j,t):
    return model.Ql[i,j,t] == (((2.0*3.14*model.k[i,j]*model.L[i,j]*(model.Ts[i,j,t]-model.Tr[i,j,t]))/math.log(model.Do[i,j]/model.Di[i,j]))/1000)*model.z[i,j,t]
model.heatloss_constraint = Constraint(model.I, model.J, model.T, rule=heatloss_constraint)

# solve the model
solver = SolverFactory("octeract");
results = solver.solve(model, tee=True)

print(f"Objective value: {model.obj():.2f}")

for t in model.T:
    for i in model.I:
        for j in model.J:
            if model.x[i, j,t]() > 0:
                print(f"From node {j} to node {i} at {t}: {model.x[i,j,t]():.2f} MWh")

# print("Production:")
# for t in model.T:
#     for i in model.I:
#         for p in model.Plants:
#             if model.p[p,i,t]() > 0:
#                 print(f"At node {i} at pp {p} at {t}: {model.p[p,i,t]():.2f} MWh")
#             if model.P_el[p,i,t].value > 0:
#                 print(f"At node {i} at pp {p} (ELEC) at {t}: {model.P_el[p,i,t].value:.2f} MWh")
print("Heatloss cost:")
for t in model.T:
    for i in model.I:
        for j in model.J:
            if model.Ql[i,j,t].value > 0:
                print(f"Loss from node {j} to node {i}: {model.Ql[i,j,t].value:.2f}")