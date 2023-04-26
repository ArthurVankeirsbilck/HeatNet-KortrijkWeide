from pyomo.environ import *
model = m = ConcreteModel()

x1 = m.x1 = Var(within=Reals, bounds=(0,1), initialize=1)
x2 = m.x2 = Var(within=Reals, bounds=(0,1), initialize=1)
x3 = m.x3 = Var(within=Reals, bounds=(0,1), initialize=None)
x4 = m.x4 = Var(within=Reals, bounds=(0,1), initialize=1)
x5 = m.x5 = Var(within=Reals, bounds=(0,1), initialize=None)

m.obj = Objective(sense=minimize, expr=42*x1 - 0.5*(100*x1*x1 + 100*x2*x2 + 100*x3*x3 + 100*x4*x4 + 100*x5*x5) + 44*x2 + 45*x3 + 47*x4 + 47.5*x5)
m.e2 = Constraint(expr=20*x1 + 12*x2 + 11*x3 + 7*x4 + 4*x5 <= 40)

results = SolverFactory("octeract").solve(m, tee=True)
print(results)
m.solutions.load_from(results)