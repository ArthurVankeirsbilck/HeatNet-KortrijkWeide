from pyomo.environ import *
model = ConcreteModel()
model.N = Set(initialize=[1,2,3])
model.T = Set(initialize=[1,2,3])
model.pmax = Param(model.N, model.T, initialize={
    (1,1):2000, (1,2):2000,(1,3):2000,
    (2,1):100,(2,2):100,(2,3):100,
    (3,1):20, (3,2):20, (3,3):20})
model.Pc = Param(model.N, model.T, initialize={
    (1,1):1,(1,2):1,(1,3):1,
    (2,1):10,(2,2):10,(2,3):10,
    (3,1):500, (3,2):500, (3,3):500})
model.Tr = Param(initialize=50)
model.d = Param(model.N, model.T,initialize={
    (1,1):50,(1,2):50,(1,3):50,
    (2,1):120,(2,2):120,(2,3):120,
    (3,1):200, (3,2):200, (3,3):200})

model.Qin = Var(model.N,model.T, within=NonNegativeReals)
model.Tin = Var(model.N,model.T, within=NonNegativeReals, bounds=(50, 120))
model.Tout = Var(model.N,model.T, within=NonNegativeReals, bounds=(50, 120))
model.I = Var(model.N,model.T, within=NonNegativeReals)
model.E = Var(model.N,model.T, within=NonNegativeReals)
model.p  =Var(model.N,model.T, within=NonNegativeReals)
model.massflow  =Var(model.T,within=NonNegativeReals, bounds=(0, 100))
model.Phi = Var(model.N,model.T,within=NonNegativeReals)
model.HL = Var(model.N,model.T, within=NonNegativeReals)
massflow = 5

def objective_rule(model):
    return sum(model.Pc[i,t]*model.p[i,t] for i in model.N for t in model.T)
model.objective = Objective(rule=objective_rule, sense=minimize)

# def heatloss(model, i):
#     if i == 1:
#         return model.HL[i,t] == 0
#     else:
#         model.Phi[i] == 2*0.414*(((model.Tout[i-1]+model.Tr)/2)-5)
#         return model.HL[i]  == (model.Phi[i]*50)/(4.18*model.massflow)
# model.heatloss = Constraint(model.N, rule=heatloss)cal


def balance_node_heatin(model, i,t):
    if i == 1:
        return model.Qin[i,t] == 0
    else:
        return model.Qin[i,t] == model.massflow[t]*4.18*(20)

model.balance_node_heatin = Constraint(model.N,model.T, rule=balance_node_heatin)

def balance_node_heatout(model, i,t):
    if i == 1:
        return model.Qin[i,t] + model.E[i,t] == model.massflow[t] *4.18*(20)
    else: 
        return model.Qin[i,t] - model.I[i,t] + model.E[i,t] == model.massflow[t] *4.18*(20)

model.balance_node_heatout = Constraint(model.N,model.T, rule=balance_node_heatout)

def demandconstraint(model, i,t):
    return model.I[i,t] - model.E[i,t] + model.p[i,t] == model.d[i,t]

model.demandconstraint = Constraint(model.N,model.T, rule=demandconstraint)

def productionconstraint(model,i,t):
    return model.p[i,t] <= model.pmax[i,t]

model.productionconstraint = Constraint(model.N,model.T, rule=productionconstraint)

def importconstraint(model,i,t):
    if i == 1:
        return model.I[i,t] <= 0
    else:
        return model.I[i,t] <=  model.massflow[t] *4.18*(20)
    
model.importconstraint= Constraint(model.N,model.T, rule=importconstraint)

solver = SolverFactory("octeract");
results = solver.solve(model,tee=True)

for t in model.T:
    print("At time {}".format(t))
    print(model.massflow[t].value)  
    for i in model.N:
        if i==1:
            print("{}:Tin:{}".format(i,50))
            print("{}:Tout:{}".format(i,model.Tout[i,t].value))
            print("{}:Qin:{}".format(i,model.Qin[i,t].value))
            print("{}:E:{}".format(i,model.E[i,t].value))
            print("{}:I:{}".format(i,model.I[i,t].value))
            print("{}:p:{}".format(i,model.p[i,t].value))
        else:  
            print("{}:Tin:{}".format(i,model.Tout[i-1,t].value))
            print("{}:Tout:{}".format(i,model.Tout[i,t].value))
            print("{}:Qin:{}".format(i,model.Qin[i,t].value))
            print("{}:E:{}".format(i,model.E[i,t].value))
            print("{}:I:{}".format(i,model.I[i,t].value))
            print("{}:p:{}".format(i,model.p[i,t].value)) 

