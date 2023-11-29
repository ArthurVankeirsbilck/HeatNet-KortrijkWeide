from pyomo.environ import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import zip_longest

######################## INPUT Data ########################
node_list = [1,2,3,4,5,6,7]
Plants = ['Plant1', 'Plant2', 'Plant3']
############################################################

####################### CONSUMPTIONS #######################

df = pd.read_csv('Data/Temperature/Consumptions.csv')

Times = len(df['KWEA'].values.tolist())
time_list = list(range(1, Times))
node_list = [1,2,3,4,5,6,7]
demand_list_node1 = df['KWEA'].values.tolist()
demand_list_node2 = df['PTI'].values.tolist()
demand_list_node3 = df['KWEP'].values.tolist()
demand_list_node4 = df['Vegitec'].values.tolist()
demand_list_node5 = df['QUBUS'].values.tolist()
demand_list_node6 = df['LAGO'].values.tolist()
demand_list_node7 = df['HangarK'].values.tolist()
demand = {}

for i in node_list:
    demand_list = globals()[f"demand_list_node{i}"]
    for time, d in zip(time_list, demand_list):
        demand[(i, time)] = d

############################################################

########################## PRICES ##########################
prices = {}

price_list_node1_Plant1 = [0.05]*8760
price_list_node1_Plant2 = [0.05]*8760
price_list_node1_Plant3 = [0.05]*8760

price_list_node2_Plant1 = [0.05]*8760
price_list_node2_Plant2 = [0.05]*8760
price_list_node2_Plant3 = [0.05]*8760

price_list_node3_Plant1 = [0.05]*8760
price_list_node3_Plant2 = [0.05]*8760
price_list_node3_Plant3 = [0.05]*8760

price_list_node4_Plant1 = [0.05]*8760
price_list_node4_Plant2 = [0.05]*8760
price_list_node4_Plant3 = [0.05]*8760

price_list_node5_Plant1 = [0.05]*8760
price_list_node5_Plant2 = [0.05]*8760
price_list_node5_Plant3 = [0.05]*8760

price_list_node6_Plant1 = [0.05]*8760
price_list_node6_Plant2 = [0.05]*8760
price_list_node6_Plant3 = [0.05]*8760

price_list_node7_Plant1 = [0.05]*8760
price_list_node7_Plant2 = [0.05]*8760
price_list_node7_Plant3 = [0.05]*8760

for i in node_list:
    for j in Plants:
        price_list = globals()[f"price_list_node{i}_{j}"]
        for time, price in zip(time_list, price_list):
            prices[(i, j, time)] = price

############################################################

#################### BACK/FORWARD FLOWS ####################
T_forward_flow = []
T_backward_flow = []

for i in range(len(demand_list_node1)-1):
    if demand_list_node1[i] < 525.7 and demand_list_node2[i] < 2697:
        T_forward_flow.append(i+1)
    else:
        T_backward_flow.append(i+1)

print(len(T_forward_flow))
print(len(T_backward_flow))
############################################################

################## PUMPPOWER COEFFICIENTS ##################
coefficients_LC = {}
df_pipesegments = pd.read_csv("LinearRegression.csv")
coefficient_list = df_pipesegments['coefficients'].values.tolist()
for node, d in zip(node_list, coefficient_list):
    coefficients_LC[node] = d

Intercepts_LC = {}
intercept_list = df_pipesegments['intercepts'].values.tolist()
for node, d in zip(node_list, intercept_list):
    Intercepts_LC[node] = d
############################################################

CHP_plants ={
    (1, 'Plant1'),(3, 'Plant1'), (6, 'Plant1')
}

HOB_plants ={
    (1, 'Plant2'),(1, 'Plant3'),
    (2, 'Plant1'),(2, 'Plant2'),(2, 'Plant3'),
    (3, 'Plant2'),(3, 'Plant3'),
    (4, 'Plant1'),(4, 'Plant2'),(4, 'Plant3'),
    (5, 'Plant1'),(5, 'Plant2'),(5, 'Plant3'),
    (6, 'Plant2'),(6, 'Plant3'),
    (7, 'Plant1'),(7, 'Plant2'),(7, 'Plant3')
}

model = ConcreteModel()
model.N = Set(initialize=node_list)
model.T = Set(initialize=time_list)
model.T_forward = Set(within=model.T, initialize=T_forward_flow)
model.T_backward = Set(within=model.T, initialize=T_backward_flow)
model.Plants = Set(initialize=Plants)
model.CHP_Plants = Set(within=model.N * model.Plants, initialize=CHP_plants)
model.HOB_Plants = Set(within=model.N * model.Plants, initialize=HOB_plants)

model.demand = Param(model.N, model.T, initialize=demand)

model.P_gen = Param(model.N,model.Plants, initialize={
    (1, 'Plant1'): 478, (1, 'Plant2'): 1000,(1, 'Plant3'): 0,
    (2, 'Plant1'): 2312,(2, 'Plant2'):   45,(2, 'Plant3'): 340,
    (3, 'Plant1'): 384,(3, 'Plant2'): 0,(3, 'Plant3'): 0,
    (4, 'Plant1'): 0,(4, 'Plant2'): 0,(4, 'Plant3'): 0,
    (5, 'Plant1'): 0,(5, 'Plant2'): 0,(5, 'Plant3'): 0,
    (6, 'Plant1'): 160,(6, 'Plant2'): 1440,(6, 'Plant3'): 0,
    (7, 'Plant1'): 0,(7, 'Plant2'): 500,(7, 'Plant3'): 0
})
ramprate_HOB = 0.05
model.ramp_rate = Param(model.N, model.Plants, initialize={
    (1, 'Plant1'): 0.05,(1, 'Plant2'): ramprate_HOB,(1, 'Plant3'): ramprate_HOB,
    (2, 'Plant1'): ramprate_HOB,(2, 'Plant2'): ramprate_HOB,(2, 'Plant3'): ramprate_HOB,
    (3, 'Plant1'): ramprate_HOB,(3, 'Plant2'):ramprate_HOB,(3, 'Plant3'): ramprate_HOB,
    (4, 'Plant1'): 0.05,(4, 'Plant2'): ramprate_HOB,(4, 'Plant3'): ramprate_HOB,
    (5, 'Plant1'): ramprate_HOB,(5, 'Plant2'): ramprate_HOB,(5, 'Plant3'): ramprate_HOB,
    (6, 'Plant1'): 0.05,(6, 'Plant2'): ramprate_HOB,(6, 'Plant3'): ramprate_HOB,
    (7, 'Plant1'): ramprate_HOB,(7, 'Plant2'): ramprate_HOB,(7, 'Plant3'): ramprate_HOB
})

model.Injectieprijs = Param(initialize=0.16)
model.Cgen = Param(model.N, model.Plants, model.T, initialize=prices)
M = 1000
model.P_el = Var(model.Plants, model.N, model.T, bounds=(0, None))
model.kappa= Var(model.N, model.Plants,model.T, within=Binary)
model.lengths = Param(model.N, initialize={1:50, 2:120,3:331,4:173,5:112,6:100,7:50})
model.coefficients = Param(model.N,initialize=coefficients_LC)
model.intercepts = Param(model.N,initialize=Intercepts_LC)
model.Ts = Param(initialize=60)
model.Tr = Param(initialize=40)
model.Cp = Param(initialize=4.18)
model.Afnamekost = Param(initialize=0.25) 
model.I = Var(model.N, model.T, within=NonNegativeReals)
model.E = Var(model.N, model.T, within=NonNegativeReals)
model.m_pipe = Var(model.N, model.T, within=NonNegativeReals)
model.Ppump= Var(model.N, model.T, within=NonNegativeReals)
model.m_N_ex = Var(model.N, model.T, within=NonNegativeReals)
model.m_N_im = Var(model.N, model.T, within=NonNegativeReals)
model.Z1 = Var(model.N, model.T, domain=Binary)
model.Z2 = Var(model.N, model.T, domain=Binary)
model.p = Var(model.Plants,model.N, model.T, within=NonNegativeReals)

### controleren
model.yA = Param(model.CHP_Plants, initialize={
    (1, 'Plant1'): 140, (3, 'Plant1'):288, (6, 'Plant1'):140
})

model.xA = Param(model.CHP_Plants, initialize={
    (1, 'Plant1'): 0, (3, 'Plant1'):0, (6, 'Plant1'):0
})

model.xB = Param(model.CHP_Plants, initialize={
    (1, 'Plant1'): 207, (3, 'Plant1'): 232, (6, 'Plant1'):140
})

model.yB = Param(model.CHP_Plants, initialize={
    (1, 'Plant1'): 112, (3, 'Plant1'): 230.4, (6, 'Plant1'):112
})

model.xC = Param(model.CHP_Plants, initialize={
    (1, 'Plant1'): 42, (3, 'Plant1'): 115.5, (6, 'Plant1'):112
})

model.yC = Param(model.CHP_Plants, initialize={
    (1, 'Plant1'): 89.6, (3, 'Plant1'): 184.32, (6, 'Plant1'):56
})

model.xD = Param(model.CHP_Plants, initialize={
    (1, 'Plant1'): 0, (3, 'Plant1'):0, (6, 'Plant1'):0
})

model.yD = Param(model.CHP_Plants, initialize={
    (1, 'Plant1'): 70, (3, 'Plant1'): 144, (6, 'Plant1'):70
})

print("Reading input data done...")

model.obj = Objective(expr=sum(((model.P_el[p,i,t])*(model.Cgen[i,p,t]/0.33)) + model.Ppump[i,t]*model.Afnamekost - model.P_el[p,i,t]*model.Injectieprijs for i in model.N for t in model.T for p in model.Plants), sense=minimize)

def pumppower(model, i ,t):
    return model.Ppump[i,t] == (model.coefficients[i]*model.m_pipe[i,t] - model.intercepts[i])/1000  

model.pumppower = Constraint(model.N, model.T, rule=pumppower) 

def demandcons(model, i, t):
    if i == 3:
        return model.I[i,t]*model.Z1[i,t] - model.E[i,t]*model.Z2[i,t] + sum(model.p[p,i,t] for p in model.Plants) == model.demand[i,t]
    else:
        return  model.I[i,t]*model.Z1[i,t] - model.E[i,t]*model.Z2[i,t] + sum(model.p[p,i,t] for p in model.Plants) == model.demand[i,t]+0.184*model.lengths[i]

model.demandcons = Constraint(model.N, model.T, rule=demandcons)

def importcons(model, i, t):
    if i == len(node_list):
        return model.I[i,t] ==  0
    else:
        return model.I[i,t] == model.m_N_im[i,t]*model.Z1[i,t] * (model.Ts - model.Tr) * model.Cp

model.importcons = Constraint(model.N, model.T_backward, rule=importcons)

def importcons2(model, i, t):
    if i == 1:
        return model.I[i,t] ==  0
    else:
        return model.I[i,t] == model.m_N_im[i,t]*model.Z1[i,t] * (model.Ts - model.Tr) * model.Cp
model.importcons2 = Constraint(model.N, model.T_forward, rule=importcons2)

def exportcons(model, i ,t):
    return model.E[i,t] == model.m_N_ex[i,t]*model.Z2[i,t] * (model.Ts - model.Tr) * model.Cp

model.exportcons = Constraint(model.N, model.T, rule=exportcons)

def import_exportcons(model, i, t):
    return model.Z1[i,t] + model.Z2[i,t] == 1

model.import_exportcons = Constraint(model.N, model.T, rule= import_exportcons)

def pipe_flow_forward(model, i,t):
    if i == 1:
        return model.m_pipe[i,t] ==  0
    else:
        return model.m_pipe[i,t] == model.m_pipe[i-1,t] + model.m_N_ex[i-1,t]*model.Z2[i-1,t]  - model.m_N_im[i-1,t]*model.Z1[i-1,t]
model.pipe_flow_forward = Constraint(model.N, model.T_forward, rule=pipe_flow_forward)

def pipe_flow_backward(model, i,t):
    if i == len(node_list):
        return model.m_pipe[i,t] ==  0
    else:
        return model.m_pipe[i,t] == model.m_pipe[i+1,t] + model.m_N_ex[i+1,t]*model.Z2[i+1,t]  - model.m_N_im[i+1,t]*model.Z1[i+1,t]
model.pipe_flow_backward = Constraint(model.N, model.T_backward, rule=pipe_flow_backward)

def pipe_flow_cons(model, i,t):
    return model.m_N_im[i,t] <= model.m_pipe[i,t]
model.pipe_flow_cons = Constraint(model.N, model.T, rule= pipe_flow_cons)

def CHP_1(model, t, i, p):
    return model.P_el[p,i,t] - model.yA[i,p] - ((model.yA[i,p]-model.yC[i,p])/(model.xB[i,p]-model.xC[i,p])) * (model.p[p,i,t]) <= 0
model.CHP_1_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_1)

def CHP_2(model, t, i, p):
    return model.P_el[p,i,t] - model.yB[i,p] - ((model.yB[i,p]-model.yC[i,p])/(model.xB[i,p]-model.xC[i,p])) * (model.p[p,i,t] - model.xB[i,p]) >= M*(model.kappa[i,p,t] - 1)
model.CHP_2_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_2)

def CHP_3(model, t, i, p):
    return model.P_el[p,i,t] - model.yC[i,p] - ((model.yC[i,p]-model.yD[i,p])/(model.xC[i,p]-model.xD[i,p])) * (model.p[p,i,t] - model.xC[i,p]) >= M*(model.kappa[i,p,t] - 1)
model.CHP_3_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_3)

def CHP_4(model, t, i, p):
    return model.yD[i,p]*model.kappa[i,p,t] <= model.P_el[p,i,t]
model.CHP_4_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_4)

def CHP_5(model, t, i, p):
    return model.P_el[p,i,t] <= model.yA[i,p]*model.kappa[i,p,t]
model.CHP_5_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_5)

def CHP_6(model, t, i, p):
    return 0 <= model.p[p,i,t]
model.CHP_6_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_6)

def CHP_7(model, t, i, p):
    return model.p[p,i,t] <= model.xB[i,p]*model.kappa[i,p,t]
model.CHP_7_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_7)

def HOB_1(model, t, i, p):
    return model.P_el[p,i,t]  ==  0
model.HOB_1_constraint = Constraint(model.T,model.HOB_Plants, rule=HOB_1)

def HOB_2(model, t, i, p):
    return model.p[p,i,t] <= model.P_gen[i,p]*model.kappa[i,p,t]
model.HOB_2_constraint = Constraint(model.T, model.HOB_Plants, rule=HOB_2)

def ramping_1(model, i,p,t):
    if t == 1:
        return Constraint.Skip
    else:
        return model.ramp_rate[i,p]*model.P_gen[i,p] >= model.p[p,i,t] - model.p[p,i,t-1]

model.ramping_1 = Constraint(model.N, model.Plants, model.T, rule=ramping_1)

def ramping_2(model, i,p,t):
    if t == 1: 
        return Constraint.Skip 
    else:
        return model.ramp_rate[i,p]*model.P_gen[i,p] >= model.p[p,i,t-1] - model.p[p,i,t]

model.ramping_2 = Constraint(model.N, model.Plants, model.T, rule=ramping_2)

# Check the model type
model_type = model.type()

# Print the model type
print("Model type:", model_type)

print("Model reading done, solving begins...")

solver = SolverFactory("gurobi", keepfiles = True);
results = solver.solve(model,tee=True)

print("Model solved, writing results...")
# model.P_gen = Param(model.N,model.Plants, initialize={
#     (1, 'Plant1'): 200, (1, 'Plant2'): 0,(1, 'Plant3'): 0,
#     (2, 'Plant1'): 2312,(2, 'Plant2'): 45,(2, 'Plant3'): 340,
#     (3, 'Plant1'): 0,(3, 'Plant2'): 0,(3, 'Plant3'): 0,
#     (4, 'Plant1'): 360,(4, 'Plant2'): 0,(4, 'Plant3'): 0,
#     (5, 'Plant1'): 0,(5, 'Plant2'): 0,(5, 'Plant3'): 0,
#     (6, 'Plant1'): 160,(6, 'Plant2'): 1440,(6, 'Plant3'): 0,
#     (7, 'Plant1'): 1000,(7, 'Plant2'): 1000,(7, 'Plant3'): 1000
# })

productions = []
productions_EL = []
Imports = []
Exports = []
Pipe_flows = []
Pumppower = []
for i in model.N:
    for p in model.Plants:
        production_intermediate = []
        productionEL_intermediate = []
        for t in model.T:
            # print("pipeflow into {}: {}".format(i,model.m_pipe[i,T].value))
            # print("Pumppower at {}: {}".format(i,model.Ppump[i,T].value))
            # print("massflow import at {}: {}".format(i,model.m_N_im[i,T].value))
            # print("massflow export at {}: {}".format(i,model.m_N_ex[i,T].value))
            production_intermediate.append(model.p[p,i,t].value)
            productionEL_intermediate.append(model.P_el[p,i,t].value)
            #create list of names
        productions.append(production_intermediate)
        productions_EL.append(productionEL_intermediate)

for i in model.N:
    Imports_intermediate = []
    Exports_intermediate = []
    Pipe_flows_intermediate = []
    Pumppower_intermediate = []
    for t in model.T:
        Pumppower_intermediate.append(model.Ppump[i,t].value)
        Imports_intermediate.append(model.I[i,t].value)
        Exports_intermediate.append(model.E[i,t].value)
        Pipe_flows_intermediate.append(model.m_pipe[i,t].value)

    Imports.append(Imports_intermediate)
    Exports.append(Exports_intermediate)
    Pipe_flows.append(Pipe_flows_intermediate)
    Pumppower.append(Pumppower_intermediate)
def writing_to_csv(list,name):
    df = pd.DataFrame(list)
    df = df.transpose()
    df.to_csv('{}.csv'.format(name), index=False)

writing_to_csv(productions, "Prod_heat_nieuw")
writing_to_csv(productions_EL, "Prod_el_nieuw")
writing_to_csv(Imports, "Imports_nieuw")
writing_to_csv(Exports, "Exports_nieuw")
writing_to_csv(Pipe_flows, "Pipe_flows_nieuw")
writing_to_csv(Pumppower, "Pumppower_nieuw")