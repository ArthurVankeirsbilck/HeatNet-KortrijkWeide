Usage:
- conda create -n ENVNAME python pip
- Packages needed:
Pyomo,
Numpy,
Matplotlib,
Pandas,
scikit-learn,
Pyarrow,
Tkinter

Run via command prompt Run.Bat, results are available in \results folder after completion.

Be considerate  with the inputs please, not 100% foolproof just yet.

The MQCQP model is designed to determine an optimal solution that not only meets the energy demand but also minimizes the overall cost of the DHS, considering the different technological options available for heat production and distribution. Through this approach, the study aims to enhance the efficiency and economic performance of prosumer LEC DHSs.

$$\min \sum_{t \in \tau} \sum_{i \in N} \sum_{p \in P} p_{i,p,t} c^{gen}_{i, p ,t} + p^{pump}_{i,t}c^{el}_t + I_{i,t}c^{DHS} \\ - P^{el}_{p,t}c^{FiT}_t$$

Eq. \ref{OF} presents the formulation of the objective or cost function, which comprises multiple components. The initial term, represented by the innermost summation, calculates the expenses incurred in generating heat using different technologies during different time intervals. The second term takes into account the costs associated with operating pumps. The third term reflects the cost of importing heat from the system. Lastly, the fourth term accounts for the revenue generated by selling produced electricity by the CHP plants to the SPOT market.

The model is subject to several constraints that ensure the system operates effectively and efficiently.

$$
        I_{i,t}\zeta^a_{i,t} - E_{i,t}\zeta^b_{i,t} + \sum_{p \in P} p_{i,p,t} = d_{i,t} +  HL^{pipe-segment}_{i \rightarrow i+1} \\
        \quad \forall i \in N, t \in \tau, p \in P
\label{demand} $$
The demand constraint, Eq. \ref{demand}, ensures that the energy demand for each consumer at each time period is met. It calculates the net energy consumed or produced by a technology based on the import and export variables, represented by $I_{i,t}$ and $E_{i,t}$ respectively, and compares it to the corresponding energy demand $d_{i,t}$. The terms $\zeta^a_{i,t}$ and $\zeta^b_{i,t}$ are binary variables that indicate whether energy is imported or exported from or to the DHS at each node for each time period. It is evident from this constraint that the model is primarily designed to regulate heat-related aspects and does not explicitly consider electricity generation or the participants own electricity consumption. The optimization solely focuses on managing the district heating system and its associated heat dynamics.

$
    I_{i,t} = m^{in}_{i,t}\zeta^a_{i,t}\Delta TC_p  \quad \forall i \in N, t \in \tau \backslash \{1\}
    \label{import}
$

$
E_{i,t} = m^{ex}_{i,t}\zeta^b_{i,t}\Delta Tc_p  \quad \forall i \in N, t \in \tau \backslash \{1\}
\label{export}
$