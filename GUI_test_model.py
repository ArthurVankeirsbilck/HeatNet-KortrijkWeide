from pyomo.environ import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import zip_longest
import json
import tkinter as tk
import time 
import os

def model(output_console):

    def check_asset(node, value, plantnumber):
        if data[node][plantnumber] == False:
            capacity = 0
        else:
            capacity = value
        return capacity

    output_console.insert(tk.END, "Reading input data...")
    output_console.see(tk.END)
    frame.update()
    with open('inputs.json', 'r') as file:
        data = json.load(file)

    ######################## INPUT Data ########################
    Plants = ['Plant1', 'Plant2', 'Plant3']
    ############################################################
    hours = round(data["Simulation Months"]*30.42*24)
    ####################### CONSUMPTIONS #######################
    df = pd.read_csv('Data/Consumptions.csv', nrows=hours)
    # df = pd.read_csv('Consumptions_nieuw.csv')

    if data["Selected Scenario"] == 1:
        exit()
    if data["Selected Scenario"] == 3:
        node_list = [1,2,3,4,5,6,7]
        Times = len(df['KWEA'].values.tolist())
        time_list = list(range(1, Times))
        demand_data = {
            'node1': df['KWEA'].values.tolist(),
            'node2': df['PTI'].values.tolist(),
            'node3': df['Penta'].values.tolist(),
            'node4': df['QUBUS'].values.tolist(),
            'node5': df['Vegitec'].values.tolist(),
            'node6': df['LAGO'].values.tolist(),
            'node7': df['Collectief'].values.tolist()
        }
    
    if data["Selected Scenario"] == 2:
        node_list = [1,2,3,4,5]
        Times = len(df['KWEA'].values.tolist())
        time_list = list(range(1, Times))
        demand_data = {
            'node1': df['KWEA'].values.tolist(),
            'node2': df['PTI'].values.tolist(),
            'node3': df['Penta'].values.tolist(),
            'node4': df['QUBUS'].values.tolist(),
            'node5': df['Vegitec'].values.tolist(),
        }

    demand = {}

    for i in node_list:
        demand_list = demand_data[f'node{i}']
        for time2, d in zip(time_list, demand_list):
            demand[(i, time2)] = d

    ############################################################

    ########################## PRICES ##########################
    prices = {}

    # Define the common price for all nodes and plants
    common_price = data["Gas Price"]/1000

    # Populate the prices dictionary with the common price
    for node in node_list:
        for plant in Plants:
            for hour in range(1, len(time_list)+1):
                prices[(node, plant, hour)] = common_price
    print(prices)
    ############################################################

    #################### BACK/FORWARD FLOWS ####################
    T_forward_flow = []
    T_backward_flow = []

    for i in range(len(demand_data['node1'])-1):
        if demand_data['node1'][i] < 525.7 and demand_data['node2'][i] < 2697:
            T_forward_flow.append(i+1)
        else:
            T_backward_flow.append(i+1)

    print(len(T_forward_flow))
    print(len(T_backward_flow))
    ############################################################

    ################## PUMPPOWER COEFFICIENTS ##################
    coefficients_LC = {}
    df_pipesegments = pd.read_csv("LinearRegression_PumpPower.csv")
    coefficient_list = df_pipesegments['coefficients'].values.tolist()
    for node, d in zip(node_list, coefficient_list):
        coefficients_LC[node] = d

    Intercepts_LC = {}
    intercept_list = df_pipesegments['intercepts'].values.tolist()
    for node, d in zip(node_list, intercept_list):
        Intercepts_LC[node] = d
    
    ramprate_HOB = 0.05
 
    model = ConcreteModel()
    model.N = Set(initialize=node_list)
    model.T = Set(initialize=time_list)
    model.T_forward = Set(within=model.T, initialize=T_forward_flow)
    model.T_backward = Set(within=model.T, initialize=T_backward_flow)
    model.Plants = Set(initialize=Plants)
    model.demand = Param(model.N, model.T, initialize=demand)
    model.Injectieprijs = Param(initialize=data["Elec Price"]/1000)
    model.Cgen = Param(model.N, model.Plants, model.T, initialize=prices)
    model.Ts = Param(initialize=data["Supplytemp"])
    model.Tr = Param(initialize=data["Returntemp"])
    model.Cp = Param(initialize=4.18)
    model.coefficients = Param(model.N,initialize=coefficients_LC)
    model.intercepts = Param(model.N,initialize=Intercepts_LC)
    model.Afnamekost = Param(initialize=data["Elec Price"]/1000) 
    model.P_el = Var(model.Plants, model.N, model.T, bounds=(0, None))
    model.kappa= Var(model.N, model.Plants,model.T, within=Binary)
    model.I = Var(model.N, model.T, within=NonNegativeReals)
    model.E = Var(model.N, model.T, within=NonNegativeReals)
    model.m_pipe = Var(model.N, model.T, within=NonNegativeReals)
    model.Ppump= Var(model.N, model.T, within=NonNegativeReals)
    model.m_N_ex = Var(model.N, model.T, within=NonNegativeReals)
    model.m_N_im = Var(model.N, model.T, within=NonNegativeReals)
    model.Z1 = Var(model.N, model.T, domain=Binary)
    model.Z2 = Var(model.N, model.T, domain=Binary)
    model.p = Var(model.Plants,model.N, model.T, within=NonNegativeReals)
    model.Gas_consumption = Var(model.Plants, model.N, model.T, within=NonNegativeReals)

    ############################################################
    if data["Selected Scenario"] == 3:
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
        plants_data = {
            (1, 'Plant1'): check_asset("Node 1", 478, 0), (1, 'Plant2'): check_asset("Node 1", 1000, 1),(1, 'Plant3'): 0,
            (2, 'Plant1'): check_asset("Node 2", 2312, 0),(2, 'Plant2'): check_asset("Node 2", 45, 1),(2, 'Plant3'): check_asset("Node 2", 340, 2),
            (3, 'Plant1'): check_asset("Node 3", 384, 0),(3, 'Plant2'): 0,(3, 'Plant3'): 0,
            (4, 'Plant1'): 0,(4, 'Plant2'): 0,(4, 'Plant3'): 0,
            (5, 'Plant1'): 0,(5, 'Plant2'): 0,(5, 'Plant3'): 0,
            (6, 'Plant1'): check_asset("Node 6", 160, 0),(6, 'Plant2'): 0,(6, 'Plant3'): 0,
            (7, 'Plant1'): check_asset("Node 7", 500, 0),(7, 'Plant2'): check_asset("Node 7", 1440, 1),(7, 'Plant3'): 0
            }
        model.CHP_Plants = Set(within=model.N * model.Plants, initialize=CHP_plants)
        model.HOB_Plants = Set(within=model.N * model.Plants, initialize=HOB_plants)
        model.P_gen = Param(model.N,model.Plants, initialize=plants_data)
        
        total_sum = sum(plants_data.values())*365*24
        summed_list_demands = sum([sum(values) for values in zip(*demand_data.values())])

        if total_sum > summed_list_demands:
            output_console.insert(tk.END, "\nEnough assets to provide heat. OK")
            output_console.see(tk.END)
            frame.update()
        else:
            output_console.insert(tk.END, "\nNot enough assets to provide heat, please change inputs.")
            output_console.see(tk.END)
            frame.update()
            time.sleep(5)
            exit(1)


        model.ramp_rate = Param(model.N, model.Plants, initialize={
            (1, 'Plant1'): 0.05,(1, 'Plant2'): ramprate_HOB,(1, 'Plant3'): ramprate_HOB,
            (2, 'Plant1'): ramprate_HOB,(2, 'Plant2'): ramprate_HOB,(2, 'Plant3'): ramprate_HOB,
            (3, 'Plant1'): ramprate_HOB,(3, 'Plant2'):ramprate_HOB,(3, 'Plant3'): ramprate_HOB,
            (4, 'Plant1'): 0.05,(4, 'Plant2'): ramprate_HOB,(4, 'Plant3'): ramprate_HOB,
            (5, 'Plant1'): ramprate_HOB,(5, 'Plant2'): ramprate_HOB,(5, 'Plant3'): ramprate_HOB,
            (6, 'Plant1'): 0.05,(6, 'Plant2'): ramprate_HOB,(6, 'Plant3'): ramprate_HOB,
            (7, 'Plant1'): ramprate_HOB,(7, 'Plant2'): ramprate_HOB,(7, 'Plant3'): ramprate_HOB
            })

        #Convex areas checked and correct
        model.yA = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 288, (3, 'Plant1'):140, (6, 'Plant1'):160
        })

        model.xA = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 0, (3, 'Plant1'):0, (6, 'Plant1'):0
        })

        model.xB = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 478, (3, 'Plant1'): 207, (6, 'Plant1'):140
        })

        model.yB = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 288, (3, 'Plant1'): 140, (6, 'Plant1'):160
        })

        model.xC = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 278, (3, 'Plant1'): 130, (6, 'Plant1'):112
        })

        model.yC = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 144, (3, 'Plant1'): 70, (6, 'Plant1'):70
        })

        model.xD = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 0, (3, 'Plant1'):0, (6, 'Plant1'):0
        })

        model.yD = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 144, (3, 'Plant1'): 70, (6, 'Plant1'):70
        })

        model.lengths = Param(model.N, initialize={1:50, 2:120,3:331,4:173,5:112,6:100,7:50})
    
    if data["Selected Scenario"] == 2:
        CHP_plants ={
        (1, 'Plant1'),(3, 'Plant1')}
        
        HOB_plants ={
        (1, 'Plant2'),(1, 'Plant3'),
        (2, 'Plant1'),(2, 'Plant2'),(2, 'Plant3'),
        (3, 'Plant2'),(3, 'Plant3'),
        (4, 'Plant1'), (4, 'Plant2'),(4, 'Plant3'),
        (5, 'Plant1'),(5, 'Plant2'),(5, 'Plant3')}

        model.CHP_Plants = Set(within=model.N * model.Plants, initialize=CHP_plants)
        model.HOB_Plants = Set(within=model.N * model.Plants, initialize=HOB_plants)
        plants_data = {
        (1, 'Plant1'): check_asset("Node 1", 478, 0), (1, 'Plant2'): check_asset("Node 1", 1000, 1),(1, 'Plant3'): 0,
        (2, 'Plant1'): check_asset("Node 2", 2312, 0),(2, 'Plant2'): check_asset("Node 2", 45, 1),(2, 'Plant3'): check_asset("Node 2", 340, 2),
        (3, 'Plant1'): check_asset("Node 3", 384, 0),(3, 'Plant2'): 0,(3, 'Plant3'): 0,
        (4, 'Plant1'): 0,(4, 'Plant2'): 0,(4, 'Plant3'): 0,
        (5, 'Plant1'): 0,(5, 'Plant2'): 0,(5, 'Plant3'): 0}
        model.P_gen = Param(model.N,model.Plants, initialize=plants_data)

        total_sum = sum(plants_data.values())*365*24
        summed_list_demands = sum([sum(values) for values in zip(*demand_data.values())])
        print(summed_list_demands)
        if total_sum > summed_list_demands:
            output_console.insert(tk.END, "\nEnough assets to provide heat. OK")
            output_console.see(tk.END)
            frame.update()
        else:
            output_console.insert(tk.END, "\nNot enough assets to provide heat, please change inputs.")
            output_console.see(tk.END)
            frame.update()
            time.sleep(5)
            exit(1)

        model.ramp_rate = Param(model.N, model.Plants, initialize={
        (1, 'Plant1'): 0.05,(1, 'Plant2'): ramprate_HOB,(1, 'Plant3'): ramprate_HOB,
        (2, 'Plant1'): ramprate_HOB,(2, 'Plant2'): ramprate_HOB,(2, 'Plant3'): ramprate_HOB,
        (3, 'Plant1'): ramprate_HOB,(3, 'Plant2'):ramprate_HOB,(3, 'Plant3'): ramprate_HOB,
        (4, 'Plant1'): 0.05,(4, 'Plant2'): ramprate_HOB,(4, 'Plant3'): ramprate_HOB,
        (5, 'Plant1'): ramprate_HOB,(5, 'Plant2'): ramprate_HOB,(5, 'Plant3'): ramprate_HOB})

        #Convex areas checked and correct
        model.yA = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 288, (3, 'Plant1'):140
        })

        model.xA = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 0, (3, 'Plant1'):0
        })

        model.xB = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 478, (3, 'Plant1'): 207
        })

        model.yB = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 288, (3, 'Plant1'): 140
        })

        model.xC = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 278, (3, 'Plant1'): 130
        })

        model.yC = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 144, (3, 'Plant1'): 70
        })

        model.xD = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 0, (3, 'Plant1'):0
        })

        model.yD = Param(model.CHP_Plants, initialize={
            (1, 'Plant1'): 144, (3, 'Plant1'): 70
        })
        
        model.lengths = Param(model.N, initialize={1:50, 2:120,3:331,4:173,5:112})

    print("Reading input data done...")
    output_console.insert(tk.END, "\nReading input data done...")
    output_console.see(tk.END)
    frame.update()  
    M = 1000
    model.obj = Objective(expr=sum((model.Ppump[i,t]*model.Afnamekost 
    - model.P_el[p,i,t]*model.Injectieprijs 
    + model.Gas_consumption[p,i,t]*(model.Cgen[i,p,t]) 
    for i in model.N for t in model.T for p in model.Plants)), sense=minimize)

    def pumppower(model, i ,t):
        return model.Ppump[i,t] == (model.coefficients[i]*model.m_pipe[i,t] - model.intercepts[i])/1000  

    model.pumppower = Constraint(model.N, model.T, rule=pumppower) 

    def demandcons(model, i, t):
        if i == 3:
            return model.I[i,t]*model.Z1[i,t] - model.E[i,t]*model.Z2[i,t] + sum(model.p[p,i,t] for p in model.Plants) == model.demand[i,t]
        else:
            return  model.I[i,t]*model.Z1[i,t] - model.E[i,t]*model.Z2[i,t] + sum(model.p[p,i,t] for p in model.Plants) == model.demand[i,t]+(data["heatloss"]/1000)*model.lengths[i]

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

    def CHP_efficiency(model, i,p,t):
        return model.Gas_consumption[p,i,t] == model.P_el[p,i,t]/0.6
    
    model.CHP_efficiency = Constraint(model.CHP_Plants, model.T, rule=CHP_efficiency)

    def HOB_efficiency(model, i,p,t):
        return model.Gas_consumption[p,i,t] == model.p[p,i,t]/0.8
    
    model.HOB_efficiency = Constraint(model.HOB_Plants, model.T, rule=HOB_efficiency)

    model_type = model.type()

    print("Model type:", model_type)
    print("Model reading done, solving begins...")

    output_console.insert(tk.END, "\nModel reading done, solving begins...")
    output_console.see(tk.END)  
    frame.update()  

    output_console.insert(tk.END, "\nModel type:{}".format(model_type))
    output_console.see(tk.END)  
    frame.update() 

    solver = SolverFactory("gurobi", keepfiles = True);
    solver.options['mipgap'] = 0.05
    results = solver.solve(model,tee=True)

    output_console.insert(tk.END, "\n Model solved Objective value: {}, \nwriting results...".format(round(model.obj.expr())))
    output_console.see(tk.END)  
    frame.update()  
    results_folder = 'results'
    def write_dict_to_csv_wide_format_filtered(data_dict, filename, filter_set, path):
        # The filter criteria now checks for both node and plant in the provided filter_set
        data_for_df = {}
        for key, values in data_dict.items():
            if key in filter_set:
                column_name = f"{key[0]}_{key[1]}"  # Converts tuple to 'Node_Plant' format
                data_for_df[column_name] = values
        df = pd.DataFrame(data_for_df)
        df.index = df.index + 1  # Assuming time period 't' starts from 1
        df.index.name = 'Time'

        folder_path = path

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
        file_path = os.path.join(folder_path, f'{filename}.csv')

        df.to_csv(file_path)

    productions = {}
    productions_EL = {}
    GC = {}

    for i in model.N:
        for p in model.Plants:
            productions[(i, p)] = []
            productions_EL[(i, p)] = []
            GC[(i, p)] = []
            for t in model.T:
                productions[(i, p)].append(model.p[p,i,t].value)
                productions_EL[(i, p)].append(model.P_el[p,i,t].value)
                GC[(i, p)].append(model.Gas_consumption[p,i,t].value)

    write_dict_to_csv_wide_format_filtered(productions_EL, "productions_EL", set(CHP_plants), results_folder)
    write_dict_to_csv_wide_format_filtered(productions, "productions_H", set(CHP_plants | HOB_plants), results_folder)
    write_dict_to_csv_wide_format_filtered(GC, "Gas_consumption", set(CHP_plants | HOB_plants), results_folder)
    Imports = {}
    Exports = {}
    Pipe_flows = {}
    Pumppower = {}

    
    def write_dict_to_csv(data_dict, filename, path):
        df = pd.DataFrame(data_dict)
        df.index = df.index + 1  # Assuming time period 't' starts from 1
        df.index.name = 'Time'
        folder_path = path

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
        file_path = os.path.join(folder_path, f'{filename}.csv')

        df.to_csv(file_path)
        
    # Assuming model.N and model.T are defined and accessible
    for i in model.N:
        Imports[i] = []
        Exports[i] = []
        Pipe_flows[i] = []
        Pumppower[i] = []
        for t in model.T:
            Pumppower[i].append(model.Ppump[i,t].value)
            Imports[i].append(model.I[i,t].value)
            Exports[i].append(model.E[i,t].value)
            Pipe_flows[i].append(model.m_pipe[i,t].value)

    
    write_dict_to_csv(Imports, "Imports", results_folder)
    write_dict_to_csv(Exports, "Exports", results_folder)
    write_dict_to_csv(Pipe_flows, "Pipe_flows", results_folder)
    write_dict_to_csv(Pumppower, "Pumppower", results_folder)

    output_dict = {
    "General": {},
    "CHP Full load hours [h]": {},
    "Exports [MWh]": {},
    "Imports [MWh]": {},
    "Total Costs [EUR]": {},
    "Total Gas Consumption [MWh]": {}
    }

    for chp_plant in CHP_plants:
        if chp_plant in productions_EL:
            output_dict["CHP Full load hours [h]"][str(chp_plant)] = round(sum(productions_EL[chp_plant]+productions[chp_plant])/(Times*(model.yA[chp_plant]+model.xB[chp_plant]))*Times,2)
            print(sum(productions_EL[chp_plant]), model.yA[chp_plant], chp_plant)
    
    for i in model.N:
        exports_sum = sum(Exports[i])
        imports_sum = sum(Imports[i])
        
        output_dict["Exports [MWh]"][str(i)] = round(exports_sum/1000,2)
        output_dict["Imports [MWh]"][str(i)] = round(imports_sum/1000,2)
    
    for i in model.N:
        plant_cost_list = []
        Gas_consumption_list = []
        for p in model.Plants:
            for t in model.T:
                plant_cost_list.append(model.Ppump[i,t].value*model.Afnamekost - model.P_el[p,i,t].value*model.Injectieprijs + model.Gas_consumption[p,i,t].value*(model.Cgen[i,p,t]))
                Gas_consumption_list.append(model.Gas_consumption[p,i,t].value)
        output_dict["Total Costs [EUR]"][str(i)] = round(sum(plant_cost_list),2)
        output_dict["Total Gas Consumption [MWh]"][str(i)] = round(sum(Gas_consumption_list)/1000,2)

    output_dict["General"]["Hours simulated [h]"] = hours
    output_dict["General"]["Total cost Heat Net [EUR]"] = round(model.obj(),2)

    file_path = os.path.join(results_folder, 'results.json')
    with open(file_path, 'w') as file:
        json.dump(output_dict, file, indent=4)

    output_console.insert(tk.END, "\nAll done. This window is about to close")
    output_console.see(tk.END)
    frame.update() 
    frame.after(5000, frame.destroy)

frame = tk.Tk()
frame.title("Simulation")

output_console = tk.Text(frame, height=20, width=70)
output_console.pack(pady=10)

start_button = tk.Button(frame, text="Start Simulation", command=lambda: model(output_console))
start_button.pack(pady=10)

frame.mainloop()



