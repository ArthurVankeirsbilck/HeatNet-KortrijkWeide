import matplotlib.pyplot as plt
import pandas as pd

spot = pd.read_csv("x.csv")

plt.rcParams.update({'font.size': 11})
plt.rcParams["figure.figsize"] = (11.69/2,8.27/2)

plt.plot(spot["1_3"].to_list(), label=r"$x_{1,3}$")
plt.plot(spot["1_4"].to_list(), label=r"$x_{1,4}$")
plt.plot(spot["1_5"].to_list(), label=r"$x_{1,5}$")
plt.plot(spot["1_6"].to_list(), label=r"$x_{1,6}$")

plt.plot(spot["2_3"].to_list(), label=r"$x_{1,3}$")
plt.plot(spot["2_4"].to_list(), label=r"$x_{1,4}$")
plt.plot(spot["2_5"].to_list(), label=r"$x_{1,5}$")
plt.plot(spot["2_6"].to_list(), label=r"$x_{1,6}$")
plt.plot(spot["2_7"].to_list(), label=r"$x_{1,7}$")


# plt.plot(P_CHPWastelist, label=r"$q_{CHP - Waste}$",color="brown")
# plt.plot(P_HOBCOALlist, label=r"$q_{HOB - Coal}$", color="tomato")
# plt.plot(P_HOBGASlist, label=r"$q_{HOB - Gas}$", color="indigo")
# plt.plot(NUSCALElist, label=r"$q_{SMR}$", color="red")
# plt.plot(P_HOBpelletlist, label=r"$q_{HOB - Pellet}$", color="green")
plt.gca().spines['right'].set_color('none')
plt.gca().spines['top'].set_color('none')
plt.xlabel("Time (days)")
plt.ylabel("Production"+r"($kWh)$")
plt.legend(loc="upper right")
plt.savefig('foo.png')
plt.show()