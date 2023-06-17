import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Data/Energy/Gas/Temp.csv")
df_LAGO = pd.read_csv("Data/Energy/Gas/Temp_LAGO.csv")
def conversion(start, stop, consumption, data, HV):
    list = []
    conslist = []
    data =data.iloc[start:stop]
    for i, row in data.iterrows():
        if row["Temp"] > 17:
            list.append(0)
        else:
            list.append(17-row["Temp"])
            
    data["HDD"] = list
    for i, row in data.iterrows():
        cons = ((row["HDD"]/sum(list))*consumption)*1000
        conslist.append(cons)
    
    data["Cons"] = conslist
    return data

dec_Collectief = conversion(0, 744, 382.980, df, 45)
jan_Collectief  = conversion(744, 1488, 484.581, df, 45)
cons_collectief = [dec_Collectief, jan_Collectief]
Collectief_dec_jan = pd.concat(cons_collectief)


dec_KWEA = conversion(0, 744, 132.169, df, 45)
jan_KWEA = conversion(744, 1488, 112.969, df, 45)
cons_KWEA = [dec_KWEA, jan_KWEA]
KWEA_dec_jan = pd.concat(cons_KWEA)

dec_Penta = conversion(0, 744, 372.587, df, 45)
jan_Penta = conversion(744, 1488, 307.188, df, 45)
cons_Penta = [dec_Penta, jan_Penta]
Penta_dec_jan = pd.concat(cons_Penta)

dec_LAGO = conversion(0, 744, 377.2891, df_LAGO, 45)
jan_LAGO = conversion(744, 1488, 362.81, df_LAGO, 45)
cons_LAGO = [dec_LAGO, jan_LAGO]
LAGO_dec_jan = pd.concat(cons_LAGO)
Total  = (dec_LAGO["Cons"].sum())
print(Total)
dec_PTI = conversion(0, 744, 156.685, df, 45)
jan_PTI = conversion(744, 1488, 210.532, df, 45)
cons_PTI = [dec_PTI, jan_PTI]
PTI_dec_jan = pd.concat(cons_PTI)


year_Vegitec = conversion(0, 9504, 120.243, df, 45)

dict = {'Collectief': Collectief_dec_jan["Cons"].to_list(), 'KWEA': KWEA_dec_jan["Cons"].to_list(), 'Penta': Penta_dec_jan["Cons"].to_list(), 'Vegitec': year_Vegitec["Cons"].iloc[0:1488].to_list(), 'LAGO': LAGO_dec_jan["Cons"].to_list(), "PTI":PTI_dec_jan["Cons"].to_list()}  
df = pd.DataFrame(dict) 
df.to_csv('Consumptions.csv')   