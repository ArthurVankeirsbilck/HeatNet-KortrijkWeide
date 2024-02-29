## Usage
- conda create -n ENVNAME python pip
- Packages needed:
Pyomo, Numpy, Matplotlib, Pandas, scikit-learn, Pyarrow, Tkinter

Run via command prompt Run.Bat, results are available in \results folder after completion.

Be considerate  with the inputs please, not 100% foolproof just yet.

## Model description
### General
The MQCQP model is designed to determine an optimal solution that not only meets the energy demand but also minimizes the overall cost of the DHS, considering the different technological options available for heat production and distribution. Through this approach, the study aims to enhance the efficiency and economic performance of prosumer LEC DHSs.

```math
\min \sum_{t \in \tau} \sum_{i \in N} \sum_{p \in P} p_{i,p,t} c^{gen}_{i, p ,t} + p^{pump}_{i,t}c^{el}_t + I_{i,t}c^{DHS} - P^{el}_{p,t}c^{FiT}_t
```

Above equation presents the formulation of the objective or cost function, which comprises multiple components. The initial term, represented by the innermost summation, calculates the expenses incurred in generating heat using different technologies during different time intervals. The second term takes into account the costs associated with operating pumps. The third term reflects the cost of importing heat from the system. Lastly, the fourth term accounts for the revenue generated by selling produced electricity by the CHP plants to the SPOT market.

The model is subject to several constraints that ensure the system operates effectively and efficiently.

```math
        I_{i,t}\zeta^a_{i,t} - E_{i,t}\zeta^b_{i,t} + \sum_{p \in P} p_{i,p,t} = d_{i,t} +  HL^{pipe-segment}_{i \rightarrow i+1}
        \quad \forall i \in N, t \in \tau, p \in P
```

The demand constraint, ensures that the energy demand for each consumer at each time period is met. It calculates the net energy consumed or produced by a technology based on the import and export variables, represented by $I_{i,t}$ and $E_{i,t}$ respectively, and compares it to the corresponding energy demand $d_{i,t}$. The terms $\zeta^a_{i,t}$ and $\zeta^b_{i,t}$ are binary variables that indicate whether energy is imported or exported from or to the DHS at each node for each time period. It is evident from this constraint that the model is primarily designed to regulate heat-related aspects and does not explicitly consider electricity generation or the participants own electricity consumption. The optimization solely focuses on managing the district heating system and its associated heat dynamics.

```math
    I_{i,t} = m^{in}_{i,t}\zeta^a_{i,t}\Delta TC_p  \quad \forall i \in N, t \in \tau \backslash \{1\}
```

```math
E_{i,t} = m^{ex}_{i,t}\zeta^b_{i,t}\Delta Tc_p  \quad \forall i \in N, t \in \tau \backslash \{1\}
```

The import constraint, determines the energy import for each technology during every time period. It is derived from the mass flow rate of energy entering node i ($m^{in}_{i,t}$) and the binary variable $\zeta^a{i,t}$, which indicates the presence of import. Similarly, the export constraint, Second eq. above, calculates the energy export for each technology at each time period. It calculates the export variable $E_{i,t}$ based on the mass flow rate of energy exiting the system at node $i$ ($m^{ex}_{i,t}$), the binary variable $\zeta^b{i,t}$ denoting the presence of export, and the temperature difference. The variable $m^{ex}_{i,t}$ represents the mass flow rate of energy entering the DHS.

```math
    \zeta^a_{i,t} + \zeta^b_{i,t} = 1 \quad \forall i \in N, t \in \tau
```

Above eq. establishes a binary relationship between the import and export variables for each node and time period. It ensures that energy is either imported or exported but not both simultaneously.

```math
    m^{DH-pipe}_{i,t} = m^{DH-pipe}_{i \pm 1,t} + m^{ex}_{i \pm 1,t}\zeta^b_{i \pm 1,t} - m^{in}_{i\pm 1,t}\zeta^a_{i\pm 1,t} 
    \quad \forall i \in N \backslash \{1\}, t \in \tau 
```

Above eq. ensures the continuity of mass flow rates within the DHS's pipes. It calculates the mass flow rate ($m^{DH-pipe}_{i,t}$) for each pipe segment at each node based on the flow rates of the preceding segment, export, and import variables. The equation represents the mass flow rate balance for each pipe segment between nodes and each time period. Regarding the bidirectional flow, the direction is determined based on the mass flow demand at each side of the network, the constraint consists of $i-1$ when forward flow is chosen and $i+1$ when backward flow is chosen.

```math
    m^{in}_{i,t} \leq m^{DH-pipe}_{i,t} \quad \forall i \in N, t \in \tau
```

Above eq. ensures that the import of energy for node technology at each time period does not exceed the available mass flow rate within the corresponding pipe segment. It guarantees that the energy supply does not exceed the transportation capacity of the DHS.

Further constraints are imposed on the variables heat and electricity production variables, $p_{p,i,t}$ and $p^{el}_{p,i,t}$, to account for the characteristics of specific technologies.

### Plant models
The feasible operating region of a CHP plant is assumed to be convex in terms of heat and power. The convexity of an operating area means that if the CHP can operate at two different points, it can also operate at any point on the line segment connecting them (Wang et al. (2015)). The polyhedral region consists of four CHP operating points. Points A and B represent the maximum electricity and heat generation, respectively, and their connecting segment defines the maximum fuel consumption. Points C and D represent the minimum electricity generation and heat generation, respectively, and their connecting segment defines the minimum fuel consumption. The segments between points A and D and between points B and C define the scope of operation of only electricity generation and maximum heat generation, respectively. Heat and electricity generation belong to the area within the above segments and are defined by equations presented below, M represents a sufficiently large number.

The constraints ensure that the electricity production $P^{el}_{p,i,t}$ is within the allowable range and dependent on the values of the specific operating points of the CHP plants denoted by $y$ and $x$ respectively.

```math
P^{el}_{p,i,t} - y^A_{g} - \frac{y^A_{g} - y^C_{g}}{x^B_{g} - x^C_{g}} \cdot (p_{p,i,t} - a_1) \leq 0, \quad  \forall i \in N, g \in P_{CHP}, t \in \tau
```

```math
    P^{el}_{p,i,t} - y^B_{g} - \frac{y^B_{g} - y^C_{g}}{x^B_{g} - x^C_{g}} \cdot p_{p,i,t} - x^B_{g} \geq M (\delta_{i,p,t}  - 1),
    \quad \forall i \in N, g \in P_{CHP}, t \in \tau
```

```math
    P^{el}_{p,i,t} - y^C_{g} - \frac{y^C_{g} - y^D_{g}}{x^C_{g} - x^D_{g}} \cdot p_{p,i,t} - x^C_{g} \geq M (\delta_{i,p,t} - 1),
    \quad \forall i \in N, g \in P_{CHP}, t \in \tau
```

```math
    0 \leq P^{el}_{p,i,t} \leq p^{max}_{i,p}\delta_{i,p,t}, \quad \forall i \in N, g \in P_{CHP}, t \in \tau
```

```math
    y^D_{g}\delta_{i,p,t} \leq  p_{p,i,t} \leq p_{i,p}^{max}\delta_{g,t},
    \quad \forall i \in N, g \in P_{CHP}, t \in \tau
```

Similar constraints are defined for other technologies, such as Heat-Only Boiler (HOB) plants, where the electricity production is set to zero ($P^{el}_{p,i,t} = 0$) and the heat production is limited by $p^{max}_{i,p}$.

```math
     p_{i,p,t} - p_{i,p,t-1} \leq RUR_{p,i,t} \quad \forall i \in N, p \in P, t \in \tau \setminus \{1\}
```

```math
 p_{i,p,t-1}- p_{i,p,t}  \leq RDR_{p,i,t}
 \quad \forall i \in N,  p \in P, t \in \tau \setminus \{1\}
```

To account for the ramping of power production between consecutive time steps, constraints the two above eq. are imposed.

### Pump Power and Heat loss calculations
Arbitrary to explain the pump power and heatloss calculations, formulas used are defined below
#### Pump Power
Linearised due to non-linear characteristics of the calculations:

```math
    v = \frac{m}{\rho_w A}
```

```math
Re_{i,j,t} = \frac{\rho_w v d}{\mu}
```

```math
    f=0.0055(1+(2\cdot 10^4 \frac{k}{d} + \frac{10^6}{Re})^{1/3})
```

```math
    \Delta p = \frac{L}{d}f\rho_w \frac{v^2}{2}
```

```math
    NW^{loss} = 2(\Delta p + p_{drop}^{HX})
```

```math
     P^{pump} = \frac{v\cdot  NW^{loss}}{\eta^{pump}}
```

#### Calculating heatloss for bonded pipes
Here, K represents the combined heat transmission factor that takes into account the heat conductivity of insulation and ground for both the return and supply pipes. The value of $T_s$, $T_r$ and $T_g$ corresponds to the supply, return and ground temperature respectively.
```math
    \Phi = 2K(\frac{T_s+T_r}{2} - T_g)
```

The value of K can be obtained by evaluating the eq. defined below, Where $R_I$ ($\frac{Km}{W}$) and $R_M$ ($\frac{Km}{W}$) represent the resistance for heat conduction in the insulation and the combined heat resistance, respectively.
```math
    K = \frac{1}{R_1+R_M}
```
The resistance for heat conduction in the insulation, $R_I$, can be determined using eq. defined below. The parameters $\lambda_I$ ($\frac{W}{mK}$),  $d_u$ (m) and $d_s$ (m) denote the heat conductivity of the pipe insulation per unit length, the outer diameter of the insulation, and the inner diameter of the insulation, respectively.

```math
    R_I = \frac{1}{2\pi\lambda_I}\ln{\frac{d_u}{d_s}}
```
The combined heat resistance, $R_M$, is calculated using eq. defined below. In this equation, $\lambda_g$ ($\frac{W}{mK}$) represents the heat conductivity of the ground per unit length, h (m) denotes the depth of the center of the pipes to the surface, and  b (m) represents the distance between the centers of the bonded pipes.

```math
    R_M = \frac{1}{2\pi\lambda_g}\ln{\sqrt{1+4(\frac{h'}{b})^2}}
```

Here, $h' = h+\frac{\lambda_g}{\alpha}$ represents the corrected depth of the pipe, where $\alpha$ ($\frac{W}{m^2K}$) is the heat transfer coefficient from ground surface to air.