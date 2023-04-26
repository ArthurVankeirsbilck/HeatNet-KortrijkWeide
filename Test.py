from pyomo.environ import *
import math
gas_price = 49.620 # 4/4/2023 TTF market
#Powerplants in the system
# create model object
model = ConcreteModel()

# sets
model.I = Set(initialize=[1, 2, 3])  # set of nodes
model.J = Set(initialize=[1, 2, 3])  # set of nodes
model.Plants = Set(initialize=['Plant1', 'Plant2', 'Plant3'])

# parameters
model.c = Param(model.I, model.J, initialize={
    (1, 2): 50, (1, 3): 50, (2, 1): 50, (2, 3): 50, (3, 1): 50, (3, 2): 50,
    (1, 1): 0, (2, 2): 0, (3, 3): 0  # initialize diagonal elements to zero
})  # transmission cost from i to j
model.p_max_plant = Param(model.I, model.Plants, initialize={
    (1, 'Plant1'): 0, (1, 'Plant2'): 0, (1, 'Plant3'): 0,
    (2, 'Plant1'): 300, (2, 'Plant2'): 0, (2, 'Plant3'): 0,
    (3, 'Plant1'): 800, (3, 'Plant2'): 0, (3, 'Plant3'): 0
})

model.CHP_Plants = Set(within=model.I * model.Plants, initialize={
    (1, 'Plant1'), (1, 'Plant3'),
    (2, 'Plant1'), 
    (3, 'Plant1'), (3, 'Plant3')
})

model.HOB_Plants = Set(within=model.I * model.Plants, initialize={
    (1, 'Plant2'),
    (2, 'Plant2'),
    (3, 'Plant2')
})

M=8000
Cp=4.18
massflow = 2.4

model.u = Param(model.I, model.J, initialize={(1, 2): M, (1, 3): M, (2, 1): M, (2, 3): M, (3, 1): M, (3, 2): M, (1, 1): 0, (2, 2): 0, (3, 3): 0})  # transmission capacity limit from i to j
model.d = Param(model.I, initialize={1: 400, 2: 0, 3: 400})  # net supply (supply - demand) in node i
# model.p_max = Param(model.I, initialize={1: 0, 2: 2000, 3: 0})  # maximum production capacity at node i
# model.c_gen = Param(model.I, initialize={1: 30, 2: 10, 3: 30}) # generation cost at node i
model.c_gen = Param(model.I, model.Plants, initialize={
    (1, 'Plant1'): 30, (1, 'Plant2'): 30, (1, 'Plant3'): 30,
    (2, 'Plant1'): 10, (2, 'Plant2'): 30, (2, 'Plant3'): 15,
    (3, 'Plant1'): 30, (3, 'Plant2'): 30, (3, 'Plant3'): 30
})

model.k = Param(model.I, model.J, initialize={(1, 2): 0.1, (1, 3): 0.2, (2, 1): 0.1, (2, 3): 0.3, (3, 1): 0.2, (3, 2): 0.3,(1, 1): 0, (2, 2): 0, (3, 3): 0})
model.L = Param(model.I, model.J, initialize={(1, 2): 10, (1, 3): 20, (2, 1): 10, (2, 3): 30, (3, 1): 20, (3, 2): 30,(1, 1): 0, (2, 2): 0, (3, 3): 0})
model.Do = Param(model.I, model.J, initialize={(1, 2): 0.2, (1, 3): 0.3, (2, 1): 0.2, (2, 3): 0.4, (3, 1): 0.3, (3, 2): 0.4,(1, 1): 0.4, (2, 2): 0.4, (3, 3): 0.4})
model.Di = Param(model.I, model.J, initialize={(1, 2): 0.1, (1, 3): 0.2, (2, 1): 0.1, (2, 3): 0.3, (3, 1): 0.2, (3, 2): 0.3,(1, 1): 0.1, (2, 2): 0.1, (3, 3): 0.1})

# variables
model.x = Var(model.I, model.J, bounds=(0, None))  # power transmission from i to j
model.p = Var(model.Plants, model.I, bounds=(0, None))  # production at node i
model.CQl = Var(model.I, model.J, bounds=(0, None))
model.Ql = Var(model.I, model.J, bounds=(0, None))
model.z = Var(model.I, model.J, domain=Binary)
model.demand_plus_loss = Var(model.I, bounds=(0, None))
model.Ts = Var(model.I, model.J, bounds=(60, 90))
model.Tr = Var(model.I, model.J, bounds=(50, 70))
model.y = Var(model.I, domain=Binary)
model.massflow = Var(model.I, model.J, bounds=(0, None))
M = 10000
epsilon = 0.0001
# objective
model.obj = Objective(
    expr=summation(model.c, model.x) + sum(model.c_gen[i,p]*model.p[p,i] for p in model.Plants for i in model.I) + sum(model.CQl[i,j]*model.Ql[i,j] for i in model.I for j in model.J))

def balance_constraint_rule(model, i,j):
    return sum(model.x[i, j] - model.x[j, i] for j in model.J) + sum(model.p[p,i] for p in model.Plants) == model.d[i]

model.balance_constraint = Constraint(model.I, model.J, rule=balance_constraint_rule)

def heat_flow_constraint(model, i, j):
    return Cp*model.massflow[i,j]*(model.Ts[i,j]-model.Tr[i,j]) == model.d[i]

model.heat_flow_constraint = Constraint(model.I, model.J, rule=heat_flow_constraint)

def capacity_constraint_rule(model, i, j):
    return model.x[i, j] <= model.u[i, j]*model.z[i,j]

model.capacity_constraint = Constraint(model.I, model.J, rule=capacity_constraint_rule)

def production_constraint_rule(model, i, p):
    return model.p[p,i] <= model.p_max_plant[i,p]

model.production_constraint = Constraint(model.I, model.Plants, rule=production_constraint_rule)

def heatloss_constraint(model, i, j):
    return model.Ql[i,j] == (((2.0*3.14*model.k[i,j]*model.L[i,j]*(model.Ts[i,j]-model.Tr[i,j]))/math.log(model.Do[i,j]/model.Di[i,j]))/1000)*model.z[i,j]
model.heatloss_constraint = Constraint(model.I, model.J, rule=heatloss_constraint)


def heatlosscost_constraint_rule(model, i, j):
    return model.CQl[i,j] == (
        sum(model.p[p,i]*model.c_gen[i,p] for p in model.Plants) /
        (sum(model.p[p,i] for p in model.Plants) + M * (1 - model.y[i]))
    )

model.heatlosscost_constraint = Constraint(model.I, model.J, rule=heatlosscost_constraint_rule)

def sum_power_generation_rule(model, i):
    return sum(model.p[p,i] for p in model.Plants) <= M* model.y[i]

model.sum_power_generation_constraint = Constraint(model.I, rule=sum_power_generation_rule)

def sum_power_generation_rule_2(model, i):
    return sum(model.p[p,i] for p in model.Plants) >= epsilon * model.y[i]

model.sum_power_generation_constraint_2 = Constraint(model.I, rule=sum_power_generation_rule_2)
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
                print("Supply-Return temp {} -> {}: {} <-> {}°C".format(j,i,model.Ts[i,j].value,model.Tr[i,j].value))

print("Massflows:")
for i in model.I:
    for j in model.J:
        print("From node {} to node {}: {}".format(j,i,model.massflow[i,j]))