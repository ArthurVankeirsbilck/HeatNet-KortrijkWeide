from pyomo.environ import *
model = ConcreteModel()
model.N = Set(initialize=[1,2,3])
model.T = Set(initialize=[1,2,3])

model.demand = Param(model.N, model.T, initialize={
    (1,1):100, (1,2):100, (1,3):100,
    (2,1):100, (2,2):100, (2,3):100,
    (3,1):100, (3,2):100, (3,3):100
})

model.Pmax = Param(model.N, initialize={
    1: 200, 2:200, 3:200
})

model.Cgen = Param(model.N, initialize={
    1:1, 2:5, 3:4
})

model.Ts = Param(initialize=60)
model.Tr = Param(initialize=40)
model.Cp = Param(initialize=4.18)

model.I = Var(model.N, model.T, within=NonNegativeReals)
model.E = Var(model.N, model.T, within=NonNegativeReals)
model.m_pipe = Var(model.N, model.T, within=NonNegativeReals)
model.m_N_ex = Var(model.N, model.T, within=NonNegativeReals, bounds=(0, 30))
model.m_N_im = Var(model.N, model.T, within=NonNegativeReals, bounds=(0, 30))
model.Z1 = Var(model.N, model.T, domain=Binary)
model.Z2 = Var(model.N, model.T, domain=Binary)
model.p = Var(model.N, model.T, within=NonNegativeReals)

model.obj = Objective(expr=sum(model.p[i,t]*model.Cgen[i] for i in model.N for t in model.T), sense=minimize)

def demandcons(model, i, t):
    return  model.I[i,t]*model.Z1[i,t] - model.E[i,t]*model.Z2[i,t] + model.p[i,t] == model.demand[i,t]

model.demandcons = Constraint(model.N, model.T, rule=demandcons)

def importcons(model, i, t):
    return model.I[i,t] == model.m_N_im[i,t] * (model.Ts - model.Tr) * model.Cp

model.importcons = Constraint(model.N, model.T, rule=importcons)

def exportcons(model, i ,t):
    return model.E[i,t] == model.m_N_ex[i,t] * (model.Ts - model.Tr) * model.Cp

model.exportcons = Constraint(model.N, model.T, rule=exportcons)

def import_exportcons(model, i, t):
    return model.Z1[i,t] + model.Z2[i,t] == 1

model.import_exportcons = Constraint(model.N, model.T, rule= import_exportcons)

def pipe_flow(model, i,t):
    if t == 1:
        return model.m_pipe[i,t] ==  sum(model.m_N_im[i,t] - model.m_N_ex[i,t] for i in model.N)
    else:
        return model.m_pipe[i,t] == model.m_pipe[i,t-1] + model.m_N_ex[i,t-1] - model.m_N_im[i,t-1]


model.pipe_flow = Constraint(model.N, model.T, rule= pipe_flow)

solver = SolverFactory("gurobi");
results = solver.solve(model,tee=True)

for i in model.N:
    print(model.m_pipe[i,1].value)
    print(model.m_N_im[i,1].value)
    print(model.m_N_ex[i,1].value)