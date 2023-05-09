from pyomo.environ import *
import math
import random
import csv
import pandas as pd

spot = pd.read_csv("Data/Costs/spot.csv")
spot = spot[::-1]
spot = spot.reset_index(drop=True)
spot["Euro"]=spot["Euro"].str.replace(',','.')
spot["Euro"] = pd.to_numeric(spot["Euro"])
spot["Euro"] = spot["Euro"]/1000

df = pd.read_csv("Consumptions.csv")
df.apply(pd.to_numeric)
random.seed(10)
#Data
k_SDR11 = 0.414
do_SDR11 = 0.125
di_SDR11 = 0.1022
k_PTI = 0.5454
k_DN125 = 0.5454
do_DN125 = 0.125
di_DN125 = 0.1022

k_DHnetwerk = 0.414

k_combinatie = 0.4797

def CHP_feasible_area(yA):
    xA = 0
    xB = round(yA*(180/247))
    yB = round(yA*(215/247))
    xC = round(yA*(104.8/247))
    yC = round(yA*(81/247))
    xD = 0
    yD = round(yA*(81/247));

    return xA, xB, yB, xC, yC, xD, yD

hours=10
node1_demands = df["KWEA_dec_jan"].iloc[0:hours].to_list()
node2_demands = [0]*hours
node3_demands = [300]*hours
node4_demands = df["Penta_dec_jan"].iloc[0:hours].to_list()
node5_demands = df["Vegitec_dec_jan"].iloc[0:hours].to_list()
node6_demands = [300]*hours
node7_demands = df["Collectief_dec_jan"].iloc[0:hours].to_list()
node1_costs = [86.10/1000]*hours
node2_costs = [86.10/1000]*hours
node3_costs = [0.3]*hours
node4_costs = [86.10/1000]*hours
node5_costs = [0.3]*hours
node6_costs = [212.62/1000]*hours
node7_costs = [212.62/1000]*hours
Plants = ['Plant1', 'Plant2', 'Plant3']
nodes = [1, 2, 3, 4,5,6,7]

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
model.P_elec = Param(model.T, initialize=spot["Euro"].iloc[0:hours+1].to_list())
# parameters
model.c = Param(model.I, model.J, initialize=
{(1, 1): 0, (1, 2): 0.50, (1, 3): 0.50, (1, 4): 0.50, (1, 5): 0.50, (1, 6): 0.50, (1, 7): 0.50, 
(2, 1): 0.50, (2, 2): 0, (2, 3): 0.50, (2, 4): 0.50, (2, 5): 0.50, (2, 6): 0.50, (2, 7): 0.50, 
(3, 1): 0.50, (3, 2): 0.50, (3, 3): 0, (3, 4): 0.50, (3, 5): 0.50, (3, 6): 0.50, (3, 7): 0.50, 
(4, 1): 0.50, (4, 2): 0.50, (4, 3): 0.50, (4, 4): 0, (4, 5): 0.50, (4, 6): 0.50, (4, 7): 0.50, 
(5, 1): 0.50, (5, 2): 0.50, (5, 3): 0.50, (5, 4): 0.50, (5, 5): 0, (5, 6): 0.50, (5, 7): 0.50, 
(6, 1): 0.50, (6, 2): 0.50, (6, 3): 0.50, (6, 4): 0.50, (6, 5): 0.50, (6, 6): 0, (6, 7): 0.50, 
(7, 1): 0.50, (7, 2): 0.50, (7, 3): 0.50, (7, 4): 0.50, (7, 5): 0.50, (7, 6): 0.50, (7, 7): 0}
)  # transmission cost from i to j
CHPramp = 600
HOBramp = 120
model.p_max_plant = Param(model.I, model.Plants, initialize={
    (1, 'Plant1'): 751, (1, 'Plant2'):0, (1, 'Plant3'):0,
    (2, 'Plant1'): 2312,  (2, 'Plant2'):45, (2, 'Plant3'):340,
    (3, 'Plant1'): 0, (3, 'Plant2'):0,(3, 'Plant3'):0,
    (4, 'Plant1'): 350, (4, 'Plant2'): 0, (4, 'Plant3'): 0,
    (5, 'Plant1'): 0, (5, 'Plant2'): 0, (5, 'Plant3'): 0,
    (6, 'Plant1'): 160, (6, 'Plant2'): 0, (6, 'Plant3'): 0,
    (7, 'Plant1'): 0, (7, 'Plant2'): 0, (7, 'Plant3'): 0
})

model.ramp_rate = Param(model.I, model.Plants, initialize={
    (1, 'Plant1'): CHPramp/751, (1, 'Plant2'):0, (1, 'Plant3'):0,
    (2, 'Plant1'): HOBramp/2312,  (2, 'Plant2'):45, (2, 'Plant3'):HOBramp/340,
    (3, 'Plant1'): 0, (3, 'Plant2'):0,(3, 'Plant3'):0,
    (4, 'Plant1'): 350, (4, 'Plant2'): 0, (4, 'Plant3'): 0,
    (5, 'Plant1'): 0, (5, 'Plant2'): 0, (5, 'Plant3'): 0,
    (6, 'Plant1'): HOBramp/160, (6, 'Plant2'): 0, (6, 'Plant3'): 0,
    (7, 'Plant1'): 0, (7, 'Plant2'): 0, (7, 'Plant3'): 0
})

CHP_plants ={
    (1, 'Plant1'),(4, 'Plant1')  
}
HOB_plants ={
    (1, 'Plant2'), (1, 'Plant3'),
    (2, 'Plant1'), (2, 'Plant2'), (2, 'Plant3'),
    (3, 'Plant1'), (3, 'Plant2'), (3, 'Plant3'),
    (4, 'Plant2'), (4, 'Plant3'),
    (5, 'Plant1'), (5, 'Plant2'), (5, 'Plant3'),
    (6, 'Plant1'), (6, 'Plant2'), (6, 'Plant3'),
    (7, 'Plant1'), (7, 'Plant2'), (7, 'Plant3')
}
model.CHP_Plants = Set(within=model.I * model.Plants, initialize=CHP_plants)

model.HOB_Plants = Set(within=model.I * model.Plants, initialize=HOB_plants)

M=8000
Cp=4.18

model.u =Param(model.I, model.J, initialize=
{(1, 1): 0, (1, 2): M, (1, 3): M, (1, 4): M, (1, 5): M, (1, 6): M, (1, 7): M,
(2, 1): M, (2, 2): 0, (2, 3): M, (2, 4): M, (2, 5): M, (2, 6): M, (2, 7): M, 
(3, 1): M, (3, 2): M, (3, 3): 0, (3, 4): M, (3, 5): M, (3, 6): M, (3, 7): M, 
(4, 1): M, (4, 2): M, (4, 3): M, (4, 4): 0, (4, 5): M, (4, 6): M, (4, 7): M, 
(5, 1): M, (5, 2): M, (5, 3): M, (5, 4): M, (5, 5): 0, (5, 6): M, (5, 7): M, 
(6, 1): M, (6, 2): M, (6, 3): M, (6, 4): M, (6, 5): M, (6, 6): 0, (6, 7): M, 
(7, 1): M, (7, 2): M, (7, 3): M, (7, 4): M, (7, 5): M, (7, 6): M, (7, 7): 0}
) #transmission capacity

model.d = Param(model.I, model.T, initialize=demands())  # net supply (supply - demand) in node i
model.c_gen = Param(model.I, model.Plants, model.T, initialize=gencosts())

model.k = Param(model.I, model.J, initialize=
{(1, 1): 0, (1, 2): k_SDR11, (1, 3): k_DHnetwerk, (1, 4): k_combinatie, (1, 5): k_DHnetwerk, (1, 6): k_DHnetwerk, (1, 7): k_DHnetwerk,
(2, 1): k_SDR11, (2, 2): 0, (2, 3): k_PTI, (2, 4): k_combinatie, (2, 5): k_DHnetwerk, (2, 6): k_DHnetwerk, (2, 7): k_DHnetwerk, 
(3, 1): k_DHnetwerk, (3, 2): k_PTI, (3, 3): 0, (3, 4): k_DHnetwerk, (3, 5): k_DHnetwerk, (3, 6): k_DHnetwerk, (3, 7): k_DHnetwerk, 
(4, 1): k_combinatie, (4, 2): k_combinatie, (4, 3): k_DHnetwerk, (4, 4): 0, (4, 5): k_DHnetwerk, (4, 6): k_DHnetwerk, (4, 7): k_DHnetwerk, 
(5, 1): k_DHnetwerk, (5, 2): k_DHnetwerk, (5, 3): k_DHnetwerk, (5, 4): k_DHnetwerk, (5, 5): 0, (5, 6): k_DHnetwerk, (5, 7): k_DHnetwerk, 
(6, 1): k_DHnetwerk, (6, 2): k_DHnetwerk, (6, 3): k_DHnetwerk, (6, 4): k_DHnetwerk, (6, 5): k_DHnetwerk, (6, 6): 0, (6, 7): k_DHnetwerk, 
(7, 1): k_DHnetwerk, (7, 2): k_DHnetwerk, (7, 3): k_DHnetwerk, (7, 4): k_DHnetwerk, (7, 5): k_DHnetwerk, (7, 6): k_DHnetwerk, (7, 7): 0})

model.L = Param(model.I, model.J, initialize=
{(1, 1): 0, (1, 2): 50, (1, 3): 50, (1, 4): 50, (1, 5): 50, (1, 6): 50, (1, 7): 50, 
(2, 1): 50, (2, 2): 0, (2, 3): 50, (2, 4): 50, (2, 5): 50, (2, 6): 50, (2, 7): 50, 
(3, 1): 50, (3, 2): 50, (3, 3): 0, (3, 4): 50, (3, 5): 50, (3, 6): 50, (3, 7): 50, 
(4, 1): 50, (4, 2): 50, (4, 3): 50, (4, 4): 0, (4, 5): 50, (4, 6): 50, (4, 7): 50, 
(5, 1): 50, (5, 2): 50, (5, 3): 50, (5, 4): 50, (5, 5): 0, (5, 6): 50, (5, 7): 50, 
(6, 1): 50, (6, 2): 50, (6, 3): 50, (6, 4): 50, (6, 5): 50, (6, 6): 0, (6, 7): 50, 
(7, 1): 50, (7, 2): 50, (7, 3): 50, (7, 4): 50, (7, 5): 50, (7, 6): 50, (7, 7): 0})

model.Do = Param(model.I, model.J, initialize=
{(1, 1): do_DN125, (1, 2): do_DN125, (1, 3): do_DN125, (1, 4): do_DN125, (1, 5): do_DN125, (1, 6): do_DN125, (1, 7): do_DN125, 
(2, 1): do_DN125, (2, 2): do_DN125, (2, 3): do_DN125, (2, 4): do_DN125, (2, 5): do_DN125, (2, 6): do_DN125, (2, 7): do_DN125, 
(3, 1): do_DN125, (3, 2): do_DN125, (3, 3): do_DN125, (3, 4): do_DN125, (3, 5): do_DN125, (3, 6): do_DN125, (3, 7): do_DN125, 
(4, 1): do_DN125, (4, 2): do_DN125, (4, 3): do_DN125, (4, 4): do_DN125, (4, 5): do_DN125, (4, 6): do_DN125, (4, 7): do_DN125, 
(5, 1): do_DN125, (5, 2): do_DN125, (5, 3): do_DN125, (5, 4): do_DN125, (5, 5): do_DN125, (5, 6): do_DN125, (5, 7): do_DN125, 
(6, 1): do_DN125, (6, 2): do_DN125, (6, 3): do_DN125, (6, 4): do_DN125, (6, 5): do_DN125, (6, 6): do_DN125, (6, 7): do_DN125, 
(7, 1): do_DN125, (7, 2): do_DN125, (7, 3): do_DN125, (7, 4): do_DN125, (7, 5): do_DN125, (7, 6): do_DN125, (7, 7): do_DN125}
)

model.Di = Param(model.I, model.J, initialize=
{(1, 1): di_DN125, (1, 2): di_DN125, (1, 3): di_DN125, (1, 4): di_DN125, (1, 5): di_DN125, (1, 6): di_DN125, (1, 7): di_DN125, 
(2, 1): di_DN125, (2, 2): di_DN125, (2, 3): di_DN125, (2, 4): di_DN125, (2, 5): di_DN125, (2, 6): di_DN125, (2, 7): di_DN125, 
(3, 1): di_DN125, (3, 2): di_DN125, (3, 3): di_DN125, (3, 4): di_DN125, (3, 5): di_DN125, (3, 6): di_DN125, (3, 7): di_DN125, 
(4, 1): di_DN125, (4, 2): di_DN125, (4, 3): di_DN125, (4, 4): di_DN125, (4, 5): di_DN125, (4, 6): di_DN125, (4, 7): di_DN125, 
(5, 1): di_DN125, (5, 2): di_DN125, (5, 3): di_DN125, (5, 4): di_DN125, (5, 5): di_DN125, (5, 6): di_DN125, (5, 7): di_DN125, 
(6, 1): di_DN125, (6, 2): di_DN125, (6, 3): di_DN125, (6, 4): di_DN125, (6, 5): di_DN125, (6, 6): di_DN125, (6, 7): di_DN125, 
(7, 1): di_DN125, (7, 2): di_DN125, (7, 3): di_DN125, (7, 4): di_DN125, (7, 5): di_DN125, (7, 6): di_DN125, (7, 7): di_DN125}
)

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
model.Cramp= Var(model.Plants, model.I, model.T, bounds=(0, None))
model.v = Var(model.I, model.J, model.T, bounds=(0, None))
model.Re = Var(model.I, model.J, model.T, bounds=(0, None))
model.Dp = Var(model.I, model.J, model.T, bounds=(0, None))
model.NWloss = Var(model.I, model.J, model.T, bounds=(0, None))
model.Ppump= Var(model.I, model.J, model.T, bounds=(0, None))
# model.f= Var(model.I, model.J, model.T, bounds=(0, None))
M = 10000
epsilon = 0.00001
Cramping = 0.1
# objective
model.obj = Objective(
    expr=sum(model.c[i,j]*model.x[i,j,t] + model.Ppump[i,j,t] for j in model.J for i in model.I for t in model.T) + sum(model.c_gen[i,p,t]*model.p[p,i,t] - model.P_elec[t]*model.P_el[p,i,t] for p in model.Plants for i in model.I for t in model.T), sense=minimize)

def balance_constraint_rule(model, i,j,t):
    return sum(model.x[i, j, t] - model.x[j, i, t] for j in model.J) + sum(model.p[p,i,t] for p in model.Plants) == model.d[i,t]+ model.Ql[i,j,t]*model.z[i,j,t]

model.balance_constraint = Constraint(model.I, model.J, model.T , rule=balance_constraint_rule)

def heat_flow_constraint(model, i, j,t):
    return Cp*model.massflow[i,j,t]*(model.Ts[i,j,t]-model.Tr[i,j,t]) == model.d[i,t]+ model.Ql[i,j,t]*model.z[i,j,t]

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
    return model.Ql[i,j,t] == ((((2.0*3.14*model.k[i,j]*model.L[i,j]*(model.Ts[i,j,t]-model.Tr[i,j,t]))/math.log(model.Do[i,j]/model.Di[i,j]))/1000))*0.2
model.heatloss_constraint = Constraint(model.I, model.J, model.T, rule=heatloss_constraint)

def heatloss_bin1(model, i,j,t):
    return model.x[i,j,t] >= 1- M*(1-model.z[i,j,t])
model.heatloss_bin1 = Constraint(model.I, model.J, model.T, rule=heatloss_bin1)

def heatloss_bin2(model, i,j,t):
    return model.x[i,j,t] <= M*model.z[i,j,t]
model.heatloss_bin2 = Constraint(model.I, model.J, model.T, rule=heatloss_bin2)

def ramping_1(model, i,p,t):
    if t == 0:
        return Constraint.Skip
    else:
        return model.ramp_rate[i,p]*model.p_max_plant[i,p] >= model.p[p,i,t] - model.p[p,i,t-1]

model.ramping_1 = Constraint(model.I, model.Plants, model.T, rule=ramping_1)

def ramping_2(model, i,p,t):
    if t == 0: 
        return Constraint.Skip 
    else:
        return model.ramp_rate[i,p]*model.p_max_plant[i,p] >= model.p[p,i,t-1] - model.p[p,i,t]

model.ramping_2 = Constraint(model.I, model.Plants, model.T, rule=ramping_2)


def flow_speed(model, i,j,t):
    return model.v[i,j,t] == model.massflow[i,j,t]/(971.79*(3.14*((model.Di[i,j]/2)*(model.Di[i,j]/2))))

model.flow_speed = Constraint(model.I, model.J, model.T, rule=flow_speed)

def reynolds(model,i,j,t):
    return model.Re[i,j,t] == (971.79*model.v[i,j,t]*model.Di[i,j])/0.000355

model.reynolds = Constraint(model.I, model.J, model.T, rule=reynolds)

# def friction(model,i,j,t):
#     return model.f[i,j,t] == 0.0055*(1+((2*10^4)*(0.01/model.Di[i,j])+((10**6)/model.Re[i,j,t])**(1/3)))
# model.friction = Constraint(model.I, model.J, model.T, rule=friction)


def pressure_drop(model,i,j,t):
    return model.Dp[i,j,t] == (model.L[i,j]/model.Di[i,j])*0.06986*971.79*((model.v[i,j,t]**2)/2)

model.pressure_drop = Constraint(model.I, model.J, model.T, rule=pressure_drop)

def networkloss(model,i,j,t):
    return model.NWloss[i,j,t] == 2*(model.Dp[i,j,t]+60000)

model.networkloss = Constraint(model.I, model.J, model.T, rule=networkloss)

def Pumppower(model, i,j,t):
    return model.Ppump[i,j,t] == ((model.massflow[i,j,t]/971.79)*model.NWloss[i,j,t])/0.7

model.Pumppower = Constraint(model.I, model.J, model.T, rule=Pumppower)


# def ramping_3(model, i,p,t):
#     if t == model.T.first(): 
#         return model.Cramp[p,i,t] == 0
#     else:
#         return 0 <= model.Cramp[p,i,t] - ((model.p[p,i,t] - model.p[p,i,t-1])*Cramping)

# model.ramping_3 = Constraint(model.I, model.Plants, model.T, rule=ramping_3)

# def ramping_4(model, i,p,t):
#     if t == model.T.first(): 
#         return model.Cramp[p,i,t] == 0
#     else:
#         return model.Cramp[p,i,t] - ((model.p[p,i,t] - model.p[p,i,t-1])*Cramping) <= 2*1*model.kappa[i,p,t]

# model.ramping_4 = Constraint(model.I, model.Plants, model.T, rule=ramping_4)


# def ramping_5(model, i,p,t):
#     if t == model.T.first(): 
#         return model.Cramp[p,i,t] == 0
#     else:
#         return 0 <= model.Cramp[p,i,t] + ((model.p[p,i,t] - model.p[p,i,t-1])*Cramping)

# model.ramping_5 = Constraint(model.I, model.Plants, model.T, rule=ramping_5)

# def ramping_6(model, i,p,t):
#     if t == model.T.first(): 
#         return model.Cramp[p,i,t] == 0
#     else:
#         return model.Cramp[p,i,t] + ((model.p[p,i,t] - model.p[p,i,t-1])*Cramping) <= 2*1*(1-model.kappa[i,p,t])

# model.ramping_6 = Constraint(model.I, model.Plants, model.T, rule=ramping_6)


#Add Fairness constraint 
# solver = SolverFactory("knitro");
# results = solver.solve(model, options={'outlev' : 4, 'numthreads': 8},tee=True)
solver = SolverFactory("octeract");
results = solver.solve(model,tee=True)
# solver = SolverFactory("mindtpy")
# results = solver.solve(model,mip_solver="gurobi",nlp_solver="ipopt",tee=True)

print(f"Objective value: {model.obj():.2f}")

# for t in model.T:
#     for i in model.I:
#         for j in model.J:
#             if model.x[i, j,t]() > 0:
#                 print(f"From node {j} to node {i} at {t}: {model.x[i,j,t]():.2f} MWh")

print("PP:")
for t in model.T:
    for i in model.I:
        for j in model.J:
            if i == j:
                pass
            else:
                if model.v[i,j,t].value > 0:
                    print("power {} -> {}: {}".format(j,i,model.v[i,j,t].value))

# print("Heatloss cost:")
# for t in model.T:
#     for i in model.I:
#         for j in model.J:
#                 print(f"Loss from node {j} to node {i}: {model.Ql[i,j,t].value*model.z[i,j,t].value:.2f}")

# print("z:")
# for t in model.T:
#     for i in model.I:
#         for j in model.J:
#                 print(model.z[i,j,t].value)

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
                header_row.append('{}_{}'.format(j,i))
    writer.writerow(header_row)

    # Write data rows   
    for t in model.T:
        data_row = [t]
        for j in model.J:
            for i in model.I:
                if i != j:
                    data_row.append(model.x[i, j,t].value)
        writer.writerow(data_row)

with open('prod.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write header row
    header_row = ['']
    for i in model.I:
        for p in model.Plants:
            header_row.append('{}_{}_x'.format(i,p))
    writer.writerow(header_row)

    # Write data rows   
    for t in model.T:
        data_row = [t]
        for i in model.I:
            for p in model.Plants:
                data_row.append(model.p[p,i,t].value)
        writer.writerow(data_row)

with open('prod.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write header row
    header_row = ['']
    for i in model.I:
        for p in model.Plants:
            header_row.append('{}_{}_x'.format(i,p))
    writer.writerow(header_row)

    # Write data rows   
    for t in model.T:
        data_row = [t]
        for i in model.I:
            for p in model.Plants:
                data_row.append(model.p[p,i,t].value)
        writer.writerow(data_row)

with open('prodelec.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write header row
    header_row = ['']
    for i in model.I:
        for p in model.Plants:
            header_row.append('{}_{}'.format(i,p))
    writer.writerow(header_row)

    # Write data rows   
    for t in model.T:
        data_row = [t]
        for i in model.I:
            for p in model.Plants:
                data_row.append(model.P_el[p,i,t].value)
        writer.writerow(data_row)


with open('massflows.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write header row
    header_row = ['']
    for j in model.J:
        for i in model.I:
            if i != j:
                header_row.append('{}_{}'.format(j,i))
    writer.writerow(header_row)

    # Write data rows   
    for t in model.T:
        data_row = [t]
        for j in model.J:
            for i in model.I:
                if i != j:
                    data_row.append(model.massflow[i,j,t].value)
        writer.writerow(data_row)