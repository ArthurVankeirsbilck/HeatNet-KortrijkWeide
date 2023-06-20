import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import math

############################### PIPE LENGTH ################################
Length_1_2 = 50
Length_2_3 = 120
Length_3_4 = 331
Length_4_5 = 173
Length_5_6 = 112
Length_6_7 = 100
Length_7_8 = 50

Length_list = [Length_1_2, Length_2_3, Length_3_4, 
               Length_4_5, Length_5_6, Length_6_7, Length_7_8]
#############################################################################

################################# VARIABLES #################################
rho = 971.8
D_pipe = 0.125
A_pipe = 3.1415*(D_pipe/2)**2
dyn_visc = 0.000355
rel_roughness = 0.00004
HX_dP = 15000
#############################################################################


def Calculate_Ppump(rho, D_pipe, A_pipe, dyn_visc, rel_roughness, length, HX_dP):
################################### LISTS ###################################
    massflows = list(range(1, 41))
    speeds = []
    Re_numbers = []
    friction_factors = []
    dP = []
    NWloss = []
    volumeflows = []
    Ppump = []
#############################################################################

################################# CHECK ε/D #################################
    if (rel_roughness/D_pipe) > 0 and (rel_roughness/D_pipe) < 0.01:
        print("OK: ε/D is valid")
    else:
        print("NOT OK: ε/D is bigger than 0.01")
        exit()
#############################################################################

################################ Calculations ###############################

    for i in massflows:
        volumeflows.append(i/rho)

    for i in massflows:
        speeds.append((i/rho/A_pipe))

    for i in speeds:
        Re_numbers.append(rho*i*D_pipe/dyn_visc)

    for i in Re_numbers:
        friction_factors.append(0.0055*(1+(2*10**4*(rel_roughness/D_pipe)+(10**6/i))**(1/3)))

    for idx, i in enumerate(friction_factors):
        dP.append(length/D_pipe*i*rho*speeds[idx]**2/2)

    for i in dP:
        NWloss.append(2*i+HX_dP*2)

    for idx, i in enumerate(NWloss):
        Ppump.append(volumeflows[idx]*i)

    df = pd.DataFrame(list(zip(massflows, Ppump)),
               columns =['massflows', 'Ppump'])

    return df
#############################################################################

def linear_regression(df):
    X = df[["massflows"]]
    y = df[["Ppump"]]

    regressor = LinearRegression()
    regressor.fit(X, y)

    # Get the coefficients
    coefficients = regressor.coef_
    intercept = regressor.intercept_

    y_pred = regressor.predict(X)

    plt.scatter(X, y, color = 'red')
    plt.plot(X, regressor.predict(X), color = 'blue')
    plt.xlabel('Massflows')
    plt.ylabel('Pump Power')
    plt.savefig('m-Ppump.png')
    return(coefficients,intercept)


coefficients = []
intercepts = []

for i in Length_list:
    df = Calculate_Ppump(rho, D_pipe, A_pipe, dyn_visc, rel_roughness, i, HX_dP)
    coefficient, intercept = linear_regression(df)
    coefficients.append(coefficient.item(0))
    intercepts.append(intercept.item(0))

print(coefficients)
print(intercepts)
     
dict = {'coefficients': coefficients, 'intercepts': intercepts}  
       
df = pd.DataFrame(dict) 
df.to_csv('LinearRegression.csv')

######################## PUMP POWER CALCULATIONS DONE ######################




######################## START HEATLOSS CALCULATIONS #######################

################################# VARIABLES #################################
lamda_g = 1.5
Tg = 15
alpha = 1.72*(Tg-20)*0.33 #https://www.actahort.org/books/893/893_55.htm#:~:text=The%20soil%2Dair%20convective%20heat%20flux%20(Hs)%2C,0.94%3B%20N%3D6).
h_accent = 2 + lamda_g/alpha
b =0.01
lambda_i = 0.028
du = 0.125
ds = 0.130
Ts = 70
Tr = 50

#############################################################################

def Heatloss(lamda_g, Tg, alpha, h_accent, b, lambda_i, du, ds, Ts, Tr):
    ########################### COMBINED HEAT RESISTANCE #######################
    Rm = (1/(2*3.1415*lamda_g))*math.log(math.sqrt(1+4*(h_accent/b)**2))
    #############################################################################

    ######################## RESISTANCE FOR HEAT CONDUCTION #####################
    Ri = (1/(2*3.1415*lambda_i))*math.log(du/ds)
    #############################################################################

    ######################## COMBINDED TRANSMISSION FACTOR #####################
    K = 1/(Ri+Rm)
    #############################################################################

    ############################## HEATLOSS PU LENGTH ###########################
    Phi = 2*K*(((Ts+Tr)/2)-Tg)
    #############################################################################
    print(Phi)
    return Phi

print(Heatloss(lamda_g, Tg, alpha, h_accent, b, lambda_i, du, ds, Ts, Tr))