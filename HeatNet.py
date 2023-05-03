from pyomo.environ import *
import math
import random
import csv
random.seed(10)
#Data
k_SDR11 = 0.414
do_SDR11 = 0.125
di_SDR11 = 0.1022

k_DN125 = 0.5454
do_DN125 = 0.125
di_DN125 = 0.1022
print("start")
def CHP_feasible_area(yA):
    xA = 0
    xB = round(yA*(180/247))
    yB = round(yA*(215/247))
    xC = round(yA*(104.8/247))
    yC = round(yA*(81/247))
    xD = 0
    yD = round(yA*(81/247));

    return xA, xB, yB, xC, yC, xD, yD

hours=11
node1_demands = []
node2_demands = []
node3_demands = []
node4_demands = []
node1_costs = [1.8]*hours
node2_costs = [1.4]*hours
node3_costs = [1.0]*hours
node4_costs = [1.0]*hours
Plants = ['Plant1', 'Plant2', 'Plant3']
nodes = [1, 2, 3, 4]

#Aanpassen nummers, numerical instability due to big
for i in range(0,hours):
    n = random.randint(200,210)
    node1_demands.append(n)

for i in range(0,hours):
    n = random.randint(140,150)
    node2_demands.append(n)

for i in range(0,hours):
    n = random.randint(100,110)
    node3_demands.append(n)

for i in range(0,hours):
    n = random.randint(100,200)
    node4_demands.append(n)

def demands():
    demands_dict = {}
    #nodes
    for i in range(1, len(nodes)+1):
        #time periods
        for t in range(0, len(node1_demands)+1):
            # add demand to dictionary with node and time period as keys
            demands_dict[(i, t)] = eval(f"node{i}_demands[t-1]")
    return demands_dict

def gencosts():
    dict = {}
    # loop over nodes
    for i in range(1, len(nodes)+1):
        # loop over plants
        for t in range(0, len(node1_demands)+1):
            for p in Plants:
            # loop over time periods
                # add demand to dictionary with node, plant, and time period as keys
                dict[(i, p, t)] = eval(f"node{i}_costs[t-1]")
    return dict

T = len(node1_demands)+1
times = list(range(T))

# create model object
model = ConcreteModel()

# sets
model.T = Set(initialize=times)
model.I = Set(initialize=nodes)  # set of nodes
model.J = Set(initialize=nodes)  # set of nodes
model.Plants = Set(initialize=Plants)

# parameters
model.c = Param(model.I, model.J, initialize={
    (1, 2): 50, (1, 3): 50, (2, 1): 50, (2, 3): 50, (3, 1): 50, (3, 2): 50,
    (1, 1): 0, (2, 2): 0, (3, 3): 0, (1,4):50, (2,4):50, (3,4):50, (4,4):0, (4,1):50, (4,2):50, (4,3):50  # initialize diagonal elements to zero
})  # transmission cost from i to j
model.p_max_plant = Param(model.I, model.Plants, initialize={
    (1, 'Plant1'): 751, (1, 'Plant2'):0, (1, 'Plant3'):0,
    (2, 'Plant1'): 0,  (2, 'Plant2'):0, (2, 'Plant3'):0,
    (3, 'Plant1'): 0, (3, 'Plant2'):0,(3, 'Plant3'):0,
    (4, 'Plant1'): 350, (4, 'Plant2'): 0, (4, 'Plant3'): 0
})
CHP_plants ={
    (1, 'Plant1'),(4, 'Plant1')
    
}
HOB_plants ={
    (1, 'Plant2'), (1, 'Plant3'),
    (2, 'Plant1'), (2, 'Plant2'), (2, 'Plant3'),
    (3, 'Plant1'), (3, 'Plant2'), (3, 'Plant3'),
    (4, 'Plant2'), (4, 'Plant3')
}
model.CHP_Plants = Set(within=model.I * model.Plants, initialize=CHP_plants)

model.HOB_Plants = Set(within=model.I * model.Plants, initialize=HOB_plants)

M=8000
Cp=4.18
P_elec = 0.4


model.u = Param(model.I, model.J, initialize={(1, 2): M, (1, 3): 0, (2, 1): M, (2, 3): M, (3, 1): 0, (3, 2): M, (1, 1): 0, (2, 2): 0, (3, 3): 0, (1,4):0, (2,4):0, (3,4):M, (4,4):0, (4,1):0, (4,2):0, (4,3):M})  # transmission capacity limit from i to j
model.d = Param(model.I, model.T, initialize=demands())  # net supply (supply - demand) in node i
model.c_gen = Param(model.I, model.Plants, model.T, initialize=gencosts())

model.k = Param(model.I, model.J, initialize={(1, 2): k_SDR11, (1, 3): k_SDR11, (2, 1): k_SDR11, (2, 3): k_SDR11, (3, 1): k_SDR11, (3, 2): k_SDR11,(1, 1): 0, (2, 2): 0, (3, 3): 0, (1,4):k_SDR11, (2,4):k_SDR11, (3,4):k_SDR11, (4,4):0, (4,1):k_SDR11, (4,2):k_SDR11, (4,3):k_SDR11})
model.L = Param(model.I, model.J, initialize={(1, 2): 300, (1, 3): 300, (2, 1): 300, (2, 3): 300, (3, 1): 300, (3, 2): 300,(1, 1): 0, (2, 2): 0, (3, 3): 0, (1,4):0, (2,4):0, (3,4):300, (4,4):0, (4,1):0, (4,2):0, (4,3):300})
model.Do = Param(model.I, model.J, initialize={(1, 2): do_SDR11, (1, 3): do_SDR11, (2, 1): do_SDR11, (2, 3): do_SDR11, (3, 1): do_SDR11, (3, 2): do_SDR11,(1, 1): do_SDR11, (2, 2): do_SDR11, (3, 3): do_SDR11, (1,4):do_SDR11, (2,4):do_SDR11, (3,4):do_SDR11, (4,4):do_SDR11, (4,1):do_SDR11, (4,2):do_SDR11, (4,3):do_SDR11})
model.Di = Param(model.I, model.J, initialize={(1, 2): di_SDR11, (1, 3): di_SDR11, (2, 1): di_SDR11, (2, 3): di_SDR11, (3, 1): di_SDR11, (3, 2):di_SDR11,(1, 1): di_SDR11, (2, 2): di_SDR11, (3, 3): di_SDR11, (1,4):di_SDR11, (2,4):di_SDR11, (3,4):di_SDR11, (4,4):di_SDR11, (4,1):di_SDR11, (4,2):di_SDR11, (4,3):di_SDR11})
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
model.massflow = Var(model.I, model.J, model.T, bounds=(0, 20))
model.P_el = Var(model.Plants, model.I, model.T, bounds=(0, None))
model.kappa = Var(model.I, model.Plants, model.T, domain=Binary)
M = 10000000
epsilon = 0.0000001

# objective
model.obj = Objective(
    expr=sum(model.c[i,j]*model.x[i,j,t] + model.Ql[i,j,t]*model.z[i,j,t]  for j in model.J for i in model.I for t in model.T) + sum(model.c_gen[i,p,t]*model.p[p,i,t] - P_elec*model.P_el[p,i,t] for p in model.Plants for i in model.I for t in model.T), sense=minimize)

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
    return model.Ql[i,j,t] == ((((2.0*3.14*model.k[i,j]*model.L[i,j]*(model.Ts[i,j,t]-model.Tr[i,j,t]))/math.log(model.Do[i,j]/model.Di[i,j]))/1000))
model.heatloss_constraint = Constraint(model.I, model.J, model.T, rule=heatloss_constraint)

def heatloss_bin1(model, i,j,t):
    return model.x[i,j,t] >= 1- M*(1-model.z[i,j,t])
model.heatloss_bin1 = Constraint(model.I, model.J, model.T, rule=heatloss_bin1)

def heatloss_bin2(model, i,j,t):
    return model.x[i,j,t] <= M*model.z[i,j,t]
model.heatloss_bin2 = Constraint(model.I, model.J, model.T, rule=heatloss_bin2)
#Add Fairness constraint 
solver = SolverFactory("knitro");
results = solver.solve(model, options={'mip_outlevel' : 2, 'numthreads': 8}, tee=True)

# solver = SolverFactory("mindtpy")
# results = solver.solve(model,mip_solver="gurobi",nlp_solver="ipopt",tee=True)

print(f"Objective value: {model.obj():.2f}")

for t in model.T:
    for i in model.I:
        for j in model.J:
            if model.x[i, j,t]() > 0:
                print(f"From node {j} to node {i} at {t}: {model.x[i,j,t]():.2f} MWh")

print("Temps:")
for t in model.T:
    for i in model.I:
        for j in model.J:
            if i == j:
                pass
            else:
                if model.Tr[i,j,t].value > 0:
                    print("Supply-Return temp {} -> {}: {} <-> {}°C".format(j,i,model.Ts[i,j,t].value,model.Tr[i,j,t].value))

print("Heatloss cost:")
for t in model.T:
    for i in model.I:
        for j in model.J:
                print(f"Loss from node {j} to node {i}: {model.Ql[i,j,t].value*model.z[i,j,t].value:.2f}")

print("z:")
for t in model.T:
    for i in model.I:
        for j in model.J:
                print(model.z[i,j,t].value)

with open('temps.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write header row
    header_row = ['']
    for j in model.J:
        for i in model.I:
            if i != j:
                header_row.append('{}_{}_s'.format(j,i))
                header_row.append('{}_{}_r'.format(j,i))
    writer.writerow(header_row)

    # Write data rows   
    for t in model.T:
        data_row = [t]
        for j in model.J:
            for i in model.I:
                if i != j:
                    data_row.append(model.Ts[i,j,t].value)
                    data_row.append(model.Tr[i,j,t].value)
        writer.writerow(data_row)

with open('x.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write header row
    header_row = ['']
    for j in model.J:
        for i in model.I:
            if i != j:
                header_row.append('{}_{}_x'.format(j,i))
    writer.writerow(header_row)

    # Write data rows   
    for t in model.T:
        data_row = [t]
        for j in model.J:
            for i in model.I:
                if i != j:
                    data_row.append(model.x[i, j,t].value)
        writer.writerow(data_row)