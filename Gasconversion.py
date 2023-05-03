import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Data/Energy/Gas/Temp.csv")
    
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
        cubic = (row["HDD"]/sum(list))*consumption
        cubic2 = (cubic*3600)/HV
        cons = (cubic2*0.85)/HV
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

year_Vegitec = conversion(0, 9504, 120.243, df, 45)

plt.plot(Collectief_dec_jan["Cons"], label="Collectief")
plt.plot(KWEA_dec_jan["Cons"], label="KWE A")
plt.plot(Penta_dec_jan["Cons"],label="Penta")
plt.plot(year_Vegitec["Cons"].iloc[0:1488],label="Vegitec")
plt.legend()
plt.show()