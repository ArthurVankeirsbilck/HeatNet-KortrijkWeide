from pyomo.environ import *
import math
import random
import matplotlib.pyplot as plt
hours=50
randomlist = []
randomlist2 = []
randomlist3 = []
for i in range(0,hours):
    n = random.randint(0,500)
    randomlist.append(n)

for i in range(0,hours):
    n = random.randint(0,200)
    randomlist2.append(n)

for i in range(0,hours):
    n = random.randint(0,300)
    randomlist3.append(n)

node1_demands = randomlist
node2_demands = randomlist2
node3_demands = randomlist3
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
                dict[(i, p, t)] = eval(f"node{i}_demands[t-1]")

    return dict
print(demands())
gas_price = 49.620 # 4/4/2023 TTF market
def CHP_feasible_area(yA):
    xA = 0
    xB = round(yA*(180/247))
    yB = round(yA*(215/247))
    xC = round(yA*(104.8/247))
    yC = round(yA*(81/247))
    xD = 0
    yD = round(yA*(81/247));

    return xA, xB, yB, xC, yC, xD, yD

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
    (1, 'Plant1'): 200, (1, 'Plant2'): 200, (1, 'Plant3'): 200,
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
model.x = Var(model.I, model.J, model.T, bounds=(0, None),)  # power transmission from i to j
model.p = Var(model.Plants, model.I, model.T, bounds=(0, None))  # production at node i
model.mean_c = Var()  # mean transmission cost
model.CQl = Var(model.I, model.J, model.T, bounds=(0, None))
model.Ql = Var(model.I, model.J, model.T, bounds=(0, None))
model.z = Var(model.I, model.J, model.T, domain=Binary)
model.demand_plus_loss = Var(model.I, bounds=(0, None))
model.Ts = Var(model.I, model.J, model.T, bounds=(60, 120))
model.Tr = Var(model.I, model.J, model.T, bounds=(30, 50))
model.y = Var(model.I, model.T, domain=Binary)
model.massflow = Var(model.I, model.J, model.T, bounds=(0, None))
model.P_el = Var(model.Plants, model.I, model.T, bounds=(0, None))
model.kappa = Var(model.I, model.Plants, model.T, domain=Binary)
M = 10000000
epsilon = 0.0000001

# objective
model.obj = Objective(expr=sum(model.c[i,j]*model.x[i,j,t] for j in model.J for i in model.I for t in model.T) + sum(model.c_gen[i,p,t]*model.p[p,i,t] - P_elec*model.P_el[p,i,t] for p in model.Plants for i in model.I for t in model.T) + summation(model.CQl, model.z), sense=minimize)

def balance_constraint_rule(model, i,j,t):
    return sum(model.x[i, j, t] - model.x[j, i, t] for j in model.J) + sum(model.p[p,i,t] for p in model.Plants) == model.d[i,t]

model.balance_constraint = Constraint(model.I, model.J, model.T , rule=balance_constraint_rule)

def heat_flow_constraint(model, i, j,t):
    return Cp*model.massflow[i,j,t]*(model.Ts[i,j,t]-model.Tr[i,j,t]) == model.d[i,t]

model.heat_flow_constraint = Constraint(model.I, model.J, model.T, rule=heat_flow_constraint)

def capacity_constraint_rule(model, i, j,t):
    return model.x[i, j,t] <= model.u[i, j]*model.z[i,j,t]

model.capacity_constraint = Constraint(model.I, model.J, model.T, rule=capacity_constraint_rule)

for t in model.T:
    for i in model.I:
        for p in model.Plants:
            if (i,p) in model.CHP_Plants:
                    model.cons.add(model.P_el[p,i,t] - model.p_max_plant[i,p] - ((model.p_max_plant[i,p]-CHP_feasible_area(model.p_max_plant[i,p])[2])/(CHP_feasible_area(model.p_max_plant[i,p])[0]-CHP_feasible_area(model.p_max_plant[i,p])[1])) * (model.p[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[0]) <= 0)
                    model.cons.add(model.P_el[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[2] - ((CHP_feasible_area(model.p_max_plant[i,p])[2]-CHP_feasible_area(model.p_max_plant[i,p])[4])/(CHP_feasible_area(model.p_max_plant[i,p])[1]-CHP_feasible_area(model.p_max_plant[i,p])[3])) * (model.p[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[1]) >= M*(model.kappa[i,p,t] - 1))
                    model.cons.add(model.P_el[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[4] - ((CHP_feasible_area(model.p_max_plant[i,p])[4]-CHP_feasible_area(model.p_max_plant[i,p])[6])/(CHP_feasible_area(model.p_max_plant[i,p])[3]-CHP_feasible_area(model.p_max_plant[i,p])[5])) * (model.p[p,i,t] - CHP_feasible_area(model.p_max_plant[i,p])[3]) >= M*(model.kappa[i,p,t] - 1))
                    model.cons.add(CHP_feasible_area(model.p_max_plant[i,p])[6]*model.kappa[i,p,t] <= model.P_el[p,i,t])
                    model.cons.add(model.P_el[p,i,t] <= model.p_max_plant[i,p]*model.kappa[i,p,t])
                    model.cons.add(0 <= model.p[p,i,t])
                    model.cons.add(model.p[p,i,t] <= CHP_feasible_area(model.p_max_plant[i,p])[1]*model.kappa[i,p,t])
for t in model.T:
    for i in model.I:
        for p in model.Plants:
            if (i,p) in model.HOB_Plants:
                model.cons.add(model.P_el[p,i,t]  ==  0)
                model.cons.add(model.p[p,i,t] <= model.p_max_plant[i,p]*model.kappa[i,p,t])

def heatloss_constraint(model, i, j,t):
    return model.Ql[i,j,t] == ((2.0*3.14*model.k[i,j]*model.L[i,j]*(model.Ts[i,j,t]-model.Tr[i,j,t]))/math.log(model.Do[i,j]/model.Di[i,j]))/1000
model.heatloss_constraint = Constraint(model.I, model.J, model.T, rule=heatloss_constraint)

def heatlosscost_constraint_rule(model, i, j):
    return model.CQl[i,j,t] ==model.Ql[i,j,t]*(
        sum(model.p[p,i,t]*model.c_gen[i,p,t] for p in model.Plants for t in model.T) /
        (sum(model.p[p,i,t] for p in model.Plants for t in model.T) + M * (1 - model.y[i,t]))
    )

model.heatlosscost_constraint = Constraint(model.I, model.J, rule=heatlosscost_constraint_rule)

def sum_power_generation_rule(model, i,t):
    return sum(model.p[p,i,t] for p in model.Plants) <= M* model.y[i,t]

model.sum_power_generation_constraint = Constraint(model.I, model.T, rule=sum_power_generation_rule)

def sum_power_generation_rule_2(model, i,t):
    return sum(model.p[p,i,t] for p in model.Plants) >= epsilon * model.y[i,t]

model.sum_power_generation_constraint_2 = Constraint(model.I, model.T, rule=sum_power_generation_rule_2)

solver = SolverFactory('mindtpy')
results = solver.solve(model,mip_solver='glpk', nlp_solver='ipopt',tee=True)

#Results
print(f"Objective value: {model.obj():.2f}")
for t in model.T:
    for i in model.I:
        for j in model.J:
            if model.x[i, j,t]() > 0:
                print(f"From node {j} to node {i} at {t}: {model.x[i,j,t]():.2f} MWh")

transmissions = {}
for i in model.I:
    for j in model.J:
        if i==j:
            pass
        transmissions[(i,j)] = []
        for t in model.T:
            if model.x[i, j, t]() > 0:
                transmissions[(i,j)].append(model.x[i, j, t]())
            else:
                transmissions[(i,j)].append(0)
print(transmissions)
# create the plot
fig, ax = plt.subplots()
ax.set_xlabel('Time')
ax.set_ylabel('Transmitted power (MWh)')
ax.set_title('Transmissions from all nodes')

# plot each transmission
for i in model.I:
    for j in model.J:
        if i != j and transmissions[(i,j)]:
            ax.plot(model.T, transmissions[(i,j)], label=f'From node {j} to node {i}')


ax.legend()
plt.show()

print("Production:")
for t in model.T:
    for i in model.I:
        for p in model.Plants:
            if model.p[p,i,t]() > 0:
                print(f"At node {i} at pp {p} at {t}: {model.p[p,i,t]():.2f} MWh")
            if model.P_el[p,i,t].value > 0:
                print(f"At node {i} at pp {p} (ELEC) at {t}: {model.P_el[p,i,t].value:.2f} MWh")

production = {}
for p in model.Plants:
    for i in model.I:
        production[(p,i)] = []

for t in model.T:
    for i in model.I:
        for p in model.Plants:
            if model.p[p,i,t]() > 0:
                production[(p,i)].append(model.p[p,i,t]())
            else:
                production[(p,i)].append(0)

fig, ax = plt.subplots()
for p in model.Plants:
    for i in model.I:
        ax.plot(model.T, production[(p,i)], label=f'PP {p} - Node {i}')
ax.set_xlabel('Time')
ax.set_ylabel('Production (MWh)')
ax.set_title('Production for all Power Plants and Nodes')
ax.legend()
plt.show()
print("Generation costs:")
for t in model.T:
    for i in model.I:
        for p in model.Plants:
            if model.p[p,i,t].value > 0:
                print(f"At node {i} at pp {p}: {model.p[p,i,t].value*model.c_gen[i,p,t]:.2f} $")

print("Transmission costs:")
for t in model.T:
    for i in model.I:
        for j in model.J:
            if model.x[i, j,t]() > 0:
                print(f"From node {j} to node {i}: {model.x[i,j,t].value*model.c[i, j]:.2f} $")

# print("Heatloss cost:")
# for t in model.T:
#     for i in model.I:
#         for j in model.J:
#             if model.CQl[i,j,t].value*model.z[i,j,t].value > 0:
#                 print(f"Loss from node {j} to node {i}: {model.CQl[i,j].value*model.z[i,j,t].value:.2f} $")

# print("Temps:")
# for i in model.I:
#     for j in model.J:
#         if i == j:
#             pass
#         else:
#             if model.Tr[i,j].value > 0:
#                 print("Supply-Return temp {} -> {}: {} <-> {}°C".format(j,i,model.Ts[i,j].value,model.Tr[i,j].value))

# print("massflows:")
# for i in model.I:
#     for j in model.J:
#         if i == j:
#             pass
#         else:
#             if model.massflow[i,j].value > 0:
#                 print("Supply-Return temp {} -> {}: {}".format(j,i,model.massflow[i,j].value))