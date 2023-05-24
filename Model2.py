from pyomo.environ import *
model = ConcreteModel()
model.N = Set(initialize=[1,2,3])

model.pmax = Param(model.N, initialize={1:2000, 2:100,3:20})
model.Pc = Param(model.N, initialize={1:1,2:10,3:500})
model.Tr = Param(initialize=50)
model.d = Param(model.N, initialize={1:50,2:50,1:50,3:100})

model.Qin = Var(model.N, within=NonNegativeReals)
model.Tin = Var(model.N, within=NonNegativeReals, bounds=(50, 120))
model.Tout = Var(model.N, within=NonNegativeReals, bounds=(50, 120))
model.I = Var(model.N, within=NonNegativeReals)
model.E = Var(model.N, within=NonNegativeReals)
model.p  =Var(model.N, within=NonNegativeReals)
model.massflow  =Var(within=NonNegativeReals, bounds=(0, 5))
model.Phi = Var(model.N,within=NonNegativeReals)
model.HL = Var(model.N, within=NonNegativeReals)
massflow = 5

def objective_rule(model):
    return sum(model.Pc[i]*model.p[i] for i in model.N)
model.objective = Objective(rule=objective_rule, sense=minimize)

def heatloss(model, i):
    if i == 1:
        model.HL[i] == 0
    else:
        model.Phi[i] == 2*0.414*(((model.Tout[i-1]+model.Tr)/2)-5)
        model.HL[i] = (model.Phi[i]*50)/(4.18*model.massflow)
def balance_node_heatin(model, i):
    if i == 1:
        return model.Qin[i] == 0
    else:
        return model.Qin[i] == model.massflow*4.18*((model.Tout[i-1]-model.HL[i])-model.Tr)

model.balance_node_heatin = Constraint(model.N, rule=balance_node_heatin)

def balance_node_heatout(model, i):
    if i == 1:
        return model.Qin[i] + model.E[i] == model.massflow *4.18*(model.Tout[i] - model.Tr)
    else: 
        return model.Qin[i] - model.I[i] + model.E[i] == model.massflow *4.18*(model.Tout[i] - model.Tr)

model.balance_node_heatout = Constraint(model.N, rule=balance_node_heatout)

def demandconstraint(model, i):
    return model.I[i] - model.E[i] + model.p[i] == model.d[i]

model.demandconstraint = Constraint(model.N, rule=demandconstraint)

def productionconstraint(model,i):
    return model.p[i] <= model.pmax[i]

model.productionconstraint = Constraint(model.N, rule=productionconstraint)

def importconstraint(model,i):
    if i == 1:
        return model.I[i] <= 0
    else:
        return model.I[i] <=  model.massflow *4.18*((model.Tout[i-1]-model.HL[i])-model.Tr)
    
model.importconstraint= Constraint(model.N, rule=importconstraint)

solver = SolverFactory("octeract");
results = solver.solve(model,tee=True)

for i in model.N:
    if i==1:
        print("{}:Tin:{}".format(i,50))
        print("{}:Tout:{}".format(i,model.Tout[i].value))
        print("{}:Qin:{}".format(i,model.Qin[i].value))
        print("{}:E:{}".format(i,model.E[i].value))
        print("{}:I:{}".format(i,model.I[i].value))
        print("{}:p:{}".format(i,model.p[i].value))
    else:  
        print("{}:Tin:{}".format(i,model.Tout[i-1].value))
        print("{}:Tout:{}".format(i,model.Tout[i].value))
        print("{}:Qin:{}".format(i,model.Qin[i].value))
        print("{}:E:{}".format(i,model.E[i].value))
        print("{}:I:{}".format(i,model.I[i].value))
        print("{}:p:{}".format(i,model.p[i].value))
        print("{}:HL:{}".format(i,model.HL[i].value))
        print("{}:Phi:{}".format(i,model.Phi[i].value))
        

print(model.massflow.value)