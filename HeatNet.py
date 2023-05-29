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
    
Plants = ['Plant1', 'Plant2', 'Plant3']
CHP_plants ={
    (1, 'Plant1')
}

HOB_plants ={
    (1, 'Plant2'),(1, 'Plant3'),
    (2, 'Plant1'),(2, 'Plant2'),(2, 'Plant3'),
    (3, 'Plant1'),(3, 'Plant2'),(3, 'Plant3')
}

model = ConcreteModel()
model.N = Set(initialize=[1,2,3])
model.T = Set(initialize=[1,2,3])
model.Plants = Set(initialize=Plants)
model.CHP_Plants = Set(within=model.N * model.Plants, initialize=CHP_plants)
model.HOB_Plants = Set(within=model.N * model.Plants, initialize=HOB_plants)

model.demand = Param(model.N, model.T, initialize={
    (1,1):0, (1,2):100, (1,3):100,
    (2,1):200, (2,2):100, (2,3):100,
    (3,1):400, (3,2):100, (3,3):100
})

model.P_gen = Param(model.N,model.Plants, initialize={
    (1, 'Plant1'):100,(1, 'Plant2'):100,(1, 'Plant3'):100,
    (2, 'Plant1'):100,(2, 'Plant2'):100,(2, 'Plant3'):100,
    (3, 'Plant1'):100,(3, 'Plant2'):100,(3, 'Plant3'):100,
})


model.ramp_rate = Param(model.N, model.Plants, initialize={
    (1, 'Plant1'): 0.8, (1, 'Plant2'):0.8, (1, 'Plant3'):0.8,
    (2, 'Plant1'): 0.8,  (2, 'Plant2'):0.8, (2, 'Plant3'):0.8,
    (3, 'Plant1'): 0.8, (3, 'Plant2'):0.8,(3, 'Plant3'):0.8
})

model.Cgen = Param(model.N, initialize={
    1:0.4, 2:0.5, 3:4
})
M = 1000
model.P_el = Var(model.Plants, model.N, model.T, bounds=(0, None))
model.kappa= Var(model.N, model.Plants,model.T, within=Binary)
model.Ts = Param(initialize=60)
model.Tr = Param(initialize=40)
model.Cp = Param(initialize=4.18)
model.Afnamekost = Param(initialize=0.3)
model.I = Var(model.N, model.T, within=NonNegativeReals)
model.E = Var(model.N, model.T, within=NonNegativeReals)
model.m_pipe = Var(model.N, model.T, within=NonNegativeReals)
model.Ppump= Var(model.N, model.T, within=NonNegativeReals)
model.m_N_ex = Var(model.N, model.T, within=NonNegativeReals, bounds=(0, 30))
model.m_N_im = Var(model.N, model.T, within=NonNegativeReals, bounds=(0, 30))
model.Z1 = Var(model.N, model.T, domain=Binary)
model.Z2 = Var(model.N, model.T, domain=Binary)
model.p = Var(model.Plants,model.N, model.T, within=NonNegativeReals)

model.obj = Objective(expr=sum(model.p[p,i,t]*model.Cgen[i]  + model.Ppump[i,t] + model.Afnamekost*model.I[i,t] for i in model.N for t in model.T for p in model.Plants), sense=minimize)

def pumppower(model, i ,t):
    return model.Ppump[i,t] == 166.29*model.m_pipe[i,t]

model.pumppower = Constraint(model.N, model.T, rule=pumppower) 

def demandcons(model, i, t):
    return  model.I[i,t]*model.Z1[i,t] - model.E[i,t]*model.Z2[i,t] + sum(model.p[p,i,t] for p in model.Plants) == model.demand[i,t]

model.demandcons = Constraint(model.N, model.T, rule=demandcons)

def importcons(model, i, t):
    if i == 1:
        return model.I[i,t] ==  0
    else:
        return model.I[i,t] == model.m_N_im[i,t]*model.Z1[i,t] * (model.Ts - model.Tr) * model.Cp

model.importcons = Constraint(model.N, model.T, rule=importcons)

def exportcons(model, i ,t):
    return model.E[i,t] == model.m_N_ex[i,t]*model.Z2[i,t] * (model.Ts - model.Tr) * model.Cp

model.exportcons = Constraint(model.N, model.T, rule=exportcons)

def import_exportcons(model, i, t):
    return model.Z1[i,t] + model.Z2[i,t] == 1

model.import_exportcons = Constraint(model.N, model.T, rule= import_exportcons)

def pipe_flow(model, i,t):
    if i == 1:
        return model.m_pipe[i,t] ==  0
    else:
        return model.m_pipe[i,t] == model.m_pipe[i-1,t] + model.m_N_ex[i-1,t]*model.Z2[i-1,t]  - model.m_N_im[i-1,t]*model.Z1[i-1,t]
model.pipe_flow = Constraint(model.N, model.T, rule= pipe_flow)

# def pipe_flow_cons(model, i,t):
#     return model.m_N_im[i,t] <= model.m_pipe[i,t]
# model.pipe_flow_cons = Constraint(model.N, model.T, rule= pipe_flow_cons)

def CHP_1(model, t, i, p):
    return model.P_el[p,i,t] - model.P_gen[i,p] - ((model.P_gen[i,p]-CHP_feasible_area(model.P_gen[i,p])[2])/(CHP_feasible_area(model.P_gen[i,p])[0]-CHP_feasible_area(model.P_gen[i,p])[1])) * (model.p[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[0]) <= 0
model.CHP_1_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_1)

def CHP_2(model, t, i, p):
    return model.P_el[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[2] - ((CHP_feasible_area(model.P_gen[i,p])[2]-CHP_feasible_area(model.P_gen[i,p])[4])/(CHP_feasible_area(model.P_gen[i,p])[1]-CHP_feasible_area(model.P_gen[i,p])[3])) * (model.p[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[1]) >= M*(model.kappa[i,p,t] - 1)
model.CHP_2_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_2)

def CHP_3(model, t, i, p):
    return model.P_el[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[4] - ((CHP_feasible_area(model.P_gen[i,p])[4]-CHP_feasible_area(model.P_gen[i,p])[6])/(CHP_feasible_area(model.P_gen[i,p])[3]-CHP_feasible_area(model.P_gen[i,p])[5])) * (model.p[p,i,t] - CHP_feasible_area(model.P_gen[i,p])[3]) >= M*(model.kappa[i,p,t] - 1)
model.CHP_3_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_3)

def CHP_4(model, t, i, p):
    return CHP_feasible_area(model.P_gen[i,p])[6]*model.kappa[i,p,t] <= model.P_el[p,i,t]
model.CHP_4_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_4)

def CHP_5(model, t, i, p):
    return model.P_el[p,i,t] <= model.P_gen[i,p]*model.kappa[i,p,t]
model.CHP_5_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_5)

def CHP_6(model, t, i, p):
    return 0 <= model.p[p,i,t]
model.CHP_6_constraint = Constraint(model.T, model.CHP_Plants, rule=CHP_6)

def CHP_7(model, t, i, p):
    return model.p[p,i,t] <= CHP_feasible_area(model.P_gen[i,p])[1]*model.kappa[i,p,t]
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

solver = SolverFactory("gurobi");
results = solver.solve(model,tee=True)

for i in model.N:
    print("pipeflow at {}: {}".format(i,model.m_pipe[i,1].value))
    print("Pumppower at {}: {}".format(i,model.Ppump[i,1].value))
    print("massflow import at {}: {}".format(i,model.m_N_im[i,1].value))
    print("massflow export at {}: {}".format(i,model.m_N_ex[i,1].value))
    for p in model.Plants:
        print("production at {}: {}".format(i, model.p[p,i,1].value))
