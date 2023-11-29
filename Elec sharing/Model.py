from pyomo.environ import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('afnames.csv')
df_inj = pd.read_csv('injectie.csv')
Times = len(df['KWEA'].values.tolist())
time_list = list(range(1, Times))
nodelist = ["BCE","BST1","BSTA","BST5","KWEA","KWEAD","KWEP","KWEPARKING","THEWING","THELEVEL"]
afname_list_BCE = df['BCE'].values.tolist()
afname_list_BST1 = df['BST1'].values.tolist()
afname_list_BSTA = df['BSTA'].values.tolist()
afname_list_BST5 = df['BST5'].values.tolist()
afname_list_KWEA = df['KWEA'].values.tolist()
afname_list_KWEAD = df['KWEAD'].values.tolist()
afname_list_KWEP = df['KWEP'].values.tolist()
afname_list_KWEPARKING = df['KWEPARKING'].values.tolist()
afname_list_THEWING = df['THEWING'].values.tolist()
afname_list_THELEVEL = df['THELEVEL'].values.tolist()

#BST5,KWEA,KWEAD,KWEP

injectie_list_BCE = [0]*Times
injectie_list_BST1 = [0]*Times
injectie_list_BSTA = [0]*Times
injectie_list_BST5 = df['BST5'].values.tolist()
injectie_list_KWEA = df['KWEA'].values.tolist()
injectie_list_KWEAD = df['KWEAD'].values.tolist()
injectie_list_KWEP = df['KWEP'].values.tolist()
injectie_list_KWEPARKING = [0]*Times
injectie_list_THEWING = [0]*Times
injectie_list_THELEVEL = [0]*Times

Cafname_list_BCE = [0]*Times
injectie_list_BST1 = [0]*Times
injectie_list_BSTA = [0]*Times
injectie_list_BST5 = df['BST5'].values.tolist()
injectie_list_KWEA = df['KWEA'].values.tolist()
injectie_list_KWEAD = df['KWEAD'].values.tolist()
injectie_list_KWEP = df['KWEP'].values.tolist()
injectie_list_KWEPARKING = [0]*Times
injectie_list_THEWING = [0]*Times
injectie_list_THELEVEL = [0]*Times

Cafname_list_BCE = [0.2135]*327 + [0.244837451]*1018
Cafname_list_BST1 = [0.20746818]*327 + [0.238684088]*1018
Cafname_list_BSTA = [0.2135]*327 + [0.244837451]*1018
Cafname_list_BST5 = [0.203559731]*327 + [0.226760603]*1018
Cafname_list_KWEA = [0.194930541]*327 + [0.226770857]*1018
Cafname_list_KWEAD = [0.17387]*327 + [0.765625]*1018
Cafname_list_KWEP = [0.212530209]*327 + [0.241212151]*1018
Cafname_list_KWEPARKING = [0.194930541]*327 + [0.226770857]*1018
Cafname_list_THEWING = [0.214791187]*327 + [0.247603506]*1018
Cafname_list_THELEVEL = [0.2208892947]*327 + [0.2473651751]*1018

Cinjectie = [0.1]*1345
#Prijzen
#327 in maand Maart, 1018 maand juni

afnames = {}

for i in nodelist:
    afnamelist = globals()[f"afname_list_{i}"]
    for time, afname in zip(time_list, afnamelist):
        afnames[(i, time)] = afname

# print(afnames)

injecties = {}

for i in nodelist:
    injectielist = globals()[f"injectie_list_{i}"]
    for time, injectie in zip(time_list, injectielist):
        injecties[(i, time)] = injectie

# print(injecties)

Cafnames = {}

for i in nodelist:
    Cafnamelist = globals()[f"Cafname_list_{i}"]
    for time, afname in zip(time_list, Cafnamelist):
        Cafnames[(i, time)] = afname

# print(Cafnames)

Cinjecties = {}

for i in nodelist:
    for time, injectiec in zip(time_list, Cinjectie):
        Cinjecties[(i, time)] = injectiec

# print(Cinjecties)

df_tot_inj = pd.read_csv('Total_inj.csv')
tot_inj_list = df_tot_inj["Tot Inj"].values.tolist()

Tot_inj = {}

for time, inj in zip(time_list, tot_inj_list):
    Tot_inj[(time)] = inj

print(Tot_inj)

model = ConcreteModel()
model.N = Set(initialize=nodelist)
model.T = Set(initialize=time_list)

model.Pinj = Param(model.N, model.T, initialize=injecties)

model.Pafname = Param(model.N, model.T, initialize=afnames)

model.Cafname = Param(model.N, model.T, initialize=Cafnames)

model.Cinjectie = Param(model.N, model.T, initialize=Cinjecties)

model.Pinjtot = Param(model.T, initialize=Tot_inj)

# model.Cdistr = Param(model.N, model.T, initialize={
# (1,1):3, (1,2): 3, (1,3):3,
# (2,1):3, (2,2): 3, (2,3):3,
# (3,1):3, (3,2): 3, (3,3):3})

M = 1000
model.Pafname_var  = Var(model.N, model.T, within=NonNegativeReals)
model.Pinj_var  = Var(model.N, model.T, within=NonNegativeReals)
model.W  = Var(model.N, model.T, within=NonNegativeReals)

model.Pinj_recalc = Var(model.T, within=NonNegativeReals)
model.z = Var(model.T, within=Binary)
model.obj = Objective(expr=sum(model.Pafname_var[i,t]*model.Cafname[i,t] + (model.W[i,t]*model.Pinj_recalc[t])*(model.Cafname[i,t]-model.Cinjectie[i,t]) for i in model.N for t in model.T), sense=minimize)

def demandcons(model, i, t):
    return model.Pafname_var[i,t] + model.W[i,t]*model.Pinj_recalc[t] == model.Pafname[i,t]

model.demandcons = Constraint(model.N, model.T, rule=demandcons)

def weight_cons(model,i,t):
    return sum(model.W[i,t] for i in model.N) == 1

model.weight_cons = Constraint(model.N, model.T, rule=weight_cons)

def Bin_inj_cons1(model, i, t):
    return model.Pinjtot[t]  >= sum(model.Pafname[i,t] for i in model.N) - M*(1-model.z[t])  

model.Bin_inj_cons1 = Constraint(model.N, model.T, rule=Bin_inj_cons1)


def Bin_inj_cons2(model, i, t):
    return model.Pinjtot[t] <= sum(model.Pafname[i,t] for i in model.N) + M*model.z[t]

model.Bin_inj_cons2 = Constraint(model.N, model.T, rule=Bin_inj_cons2)


def Bin_inj_cons3(model, i, t):
    return sum(model.Pafname[i,t] for i in model.N) - M*(1-model.z[t]) <= model.Pinj_recalc[t]

model.Bin_inj_cons3 = Constraint(model.N, model.T, rule=Bin_inj_cons3)

def Bin_inj_cons4(model, i, t):
    return model.Pinj_recalc[t] <= sum(model.Pafname[i,t] for i in model.N) + M*(1-model.z[t])

model.Bin_inj_cons4 = Constraint(model.N, model.T, rule=Bin_inj_cons4)

def Bin_inj_cons5(model, i, t):
    return model.Pinjtot[t] -M *model.z[t]<= model.Pinj_recalc[t]

model.Bin_inj_cons5 = Constraint(model.N, model.T, rule=Bin_inj_cons5)

def Bin_inj_cons6(model, i, t):
    return model.Pinj_recalc[t] <= model.Pinjtot[t] + M*model.z[t]

model.Bin_inj_cons6 = Constraint(model.N, model.T, rule=Bin_inj_cons6)

solver = SolverFactory("gurobi", keepfiles = True, options={"NonConvex":2});
results = solver.solve(model,tee=True)
percentages = []
Pinj_recalc_int = []
Pinj_tot_int = []

Pinj_recalc = []
Pinj_tot = []
for i in model.N:
    percentages_intermediate = []
    for t in model.T:
        percentages_intermediate.append(model.W[i,t].value)

    percentages.append(percentages_intermediate)

for t in model.T:
    Pinj_recalc_int.append(model.Pinj_recalc[t].value)

Pinj_recalc.append(Pinj_recalc_int)
Pinj_tot.append(Pinj_tot_int)

def writing_to_csv(list,name):
    df = pd.DataFrame(list)
    df = df.transpose()
    df.to_csv('{}.csv'.format(name), index=False)

writing_to_csv(Pinj_recalc, "Inj_na_sharing")
writing_to_csv(percentages, "Percentages")