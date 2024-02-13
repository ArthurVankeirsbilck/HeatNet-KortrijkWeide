import tkinter as tk 
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import json
import time
from PIL import Image, ImageTk

def on_submit():
    global scenario_var
    selected_scenario = scenario_var.get()
    if selected_scenario == 0:
        lbl.config(text="Please select a scenario before submitting.")
    else:
        lbl.config(text=f"Scenario {selected_scenario} selected.")
        printInput(selected_scenario)
frame = tk.Tk() 
frame.title("Input parameters") 
frame.geometry('1920x1080') 


image = Image.open('Images/topologydhs.png')
photo = ImageTk.PhotoImage(image)

input_frame = tk.Frame(frame)
input_frame.pack(side=tk.TOP, anchor=tk.NW)

scenario_frame = tk.Frame(input_frame)
scenario_frame.pack(side=tk.TOP, anchor=tk.CENTER)
scenario_var = tk.IntVar(value=0)  

scale_frame = tk.Frame(input_frame)
scale_frame.pack(side=tk.TOP, anchor=tk.CENTER)

months_scale = tk.Scale(scale_frame, from_=1, to=12, orient='horizontal', label='Duration')
months_scale.pack(side=tk.TOP, anchor=tk.CENTER)

pipe_data_frame = tk.Frame(input_frame)
pipe_data_frame.pack(side=tk.TOP, anchor=tk.CENTER)

# rho (Density)
rho_frame = tk.Frame(pipe_data_frame)
rho_frame.pack(side=tk.LEFT)
rho_label = tk.Label(rho_frame, text="Density (kg/m³)")
rho_label.pack()
rho_input = tk.Text(rho_frame, height=1, width=10)
rho_input.pack()
rho_input.insert(tk.END, "971.8")

# Diameter of the pipe
diameter_frame = tk.Frame(pipe_data_frame)
diameter_frame.pack(side=tk.LEFT)
diameter_label = tk.Label(diameter_frame, text="Diameter (m)")
diameter_label.pack()
diameter_input = tk.Text(diameter_frame, height=1, width=10)
diameter_input.pack()
diameter_input.insert(tk.END, "0.125")

# Dynamic viscosity
viscosity_frame = tk.Frame(pipe_data_frame)
viscosity_frame.pack(side=tk.LEFT)
viscosity_label = tk.Label(viscosity_frame, text="Dyn. Viscosity (Pa·s)")
viscosity_label.pack()
viscosity_input = tk.Text(viscosity_frame, height=1, width=10)
viscosity_input.pack()
viscosity_input.insert(tk.END, "0.000355")

# Relative roughness
roughness_frame = tk.Frame(pipe_data_frame)
roughness_frame.pack(side=tk.LEFT)
roughness_label = tk.Label(roughness_frame, text="Rel. Roughness")
roughness_label.pack()
roughness_input = tk.Text(roughness_frame, height=1, width=10)
roughness_input.pack()
roughness_input.insert(tk.END, "0.00004")

# HX pressure drop
pressure_drop_frame = tk.Frame(pipe_data_frame)
pressure_drop_frame.pack(side=tk.LEFT)
pressure_drop_label = tk.Label(pressure_drop_frame, text="HX Pressure Drop (Pa)")
pressure_drop_label.pack()
pressure_drop_input = tk.Text(pressure_drop_frame, height=1, width=10)
pressure_drop_input.pack()
pressure_drop_input.insert(tk.END, "15000")

scenario1_rb = tk.Radiobutton(scenario_frame, text="Scenario 1", variable=scenario_var, value=1)
scenario1_rb.pack(side=tk.LEFT)
scenario2_rb = tk.Radiobutton(scenario_frame, text="Scenario 2", variable=scenario_var, value=2)
scenario2_rb.pack(side=tk.LEFT)
scenario3_rb = tk.Radiobutton(scenario_frame, text="Scenario 3", variable=scenario_var, value=3)
scenario3_rb.pack(side=tk.LEFT)

def get_checkbox_states():
    checkbox_states = {}
    for node, vars_list in checkbox_vars.items():
        checkbox_states[f"Node {node}"] = [var.get() for var in vars_list]
    return checkbox_states

def plot(): 
    fig = Figure(figsize = (5, 5), 
                 dpi = 100) 
  
    y = [i**2 for i in range(101)] 
  
    plot1 = fig.add_subplot(111) 
  
    plot1.plot(y) 
   
    canvas = FigureCanvasTkAgg(fig, master = frame)   
    canvas.draw() 

    canvas.get_tk_widget().pack(side=tk.BOTTOM, anchor=tk.SE, expand=True) 

    toolbar = NavigationToolbar2Tk(canvas, frame) 
    toolbar.update() 
  
    toolbar.pack(side=tk.BOTTOM, anchor=tk.SE) 

def printInput(selected_scenario): 
    try:
        inp1 = float(inputtxt1.get(1.0, "end-1c")) 
        inp2 = float(inputtxt2.get(1.0, "end-1c"))
        inp3 = float(inputtxt3.get(1.0, "end-1c"))
        inp4 = float(inputtxt4.get(1.0, "end-1c"))
        simulation_months = months_scale.get()

        # New pipe data inputs
        rho = float(rho_input.get(1.0, "end-1c"))
        diameter = float(diameter_input.get(1.0, "end-1c"))
        viscosity = float(viscosity_input.get(1.0, "end-1c"))
        roughness = float(roughness_input.get(1.0, "end-1c"))
        pressure_drop = float(pressure_drop_input.get(1.0, "end-1c"))

        global dict
        dict = {
            "Supplytemp": inp1,
            "Returntemp": inp2,
            "Elec Price": inp3,
            "Gas Price": inp4,
            "Selected Scenario": selected_scenario,
            "Simulation Months": simulation_months,
            "Density": rho,
            "Diameter": diameter,
            "Viscosity": viscosity,
            "Relative Roughness": roughness,
            "HX Pressure Drop": pressure_drop
        }
        checkbox_states = get_checkbox_states()
        dict.update(checkbox_states)
        # Save the dictionary to a JSON file
        with open('inputs.json', 'w') as fp:
            json.dump(dict, fp)
        # Update label with valid inputs
        lbl.config(text = "Input correct: \n Supply Temp.: {}°C, Return Temp.: {}°C, Elec. Price: {}€/MWh, Gas Price: {}€/MWh \n\n This window will close now.".format(inp1, inp2, inp3,inp4))
        frame.after(3000, frame.destroy)
    except ValueError:
        # If inputs are not valid floats, update label to indicate invalid input
        lbl.config(text = "Invalid input. Please enter valid floating-point numbers.")

# Creating frames for each input to align labels and textboxes horizontally
input1_frame = tk.Frame(input_frame)
input1_frame.pack(side=tk.LEFT)

input2_frame = tk.Frame(input_frame)
input2_frame.pack(side=tk.LEFT)

input3_frame = tk.Frame(input_frame)
input3_frame.pack(side=tk.LEFT)

input4_frame = tk.Frame(input_frame)
input4_frame.pack(side=tk.LEFT)

label1 = tk.Label(input1_frame, text="Supply Temp (°C)")
label1.pack()
inputtxt1 = tk.Text(input1_frame, height = 3, width = 10) 
inputtxt1.pack()

label2 = tk.Label(input2_frame, text="Return Temp (°C)")
label2.pack()
inputtxt2 = tk.Text(input2_frame, height = 3, width = 10) 
inputtxt2.pack()

label3 = tk.Label(input3_frame, text="Elec. Price (€/kWh)")
label3.pack()
inputtxt3 = tk.Text(input3_frame, height = 3, width = 10) 
inputtxt3.pack()

label4 = tk.Label(input4_frame, text="Gas Price (€/kWh)")
label4.pack()
inputtxt4 = tk.Text(input4_frame, height = 3, width = 10) 
inputtxt4.pack()

printButton = tk.Button(input_frame, text="Submit", command=on_submit)
printButton.pack(side=tk.LEFT)

lbl = tk.Label(frame, text = "") 
lbl.pack()

canvas = tk.Canvas(frame, width=image.width, height=image.height)
canvas.pack()

canvas.create_image(0, 0, image=photo, anchor=tk.NW)

def create_checkbox(x, y, text, var_dict, node):
    var = tk.BooleanVar()
    checkbutton = tk.Checkbutton(frame, variable=var, text=text, bg="white", anchor="w")
    canvas.create_window(x, y, window=checkbutton, anchor='nw')
    var_dict[node].append(var)  # Store the variable in the dictionary
    return y + 20  # Return the new y position for the next checkbox

    
    return var  # Returning the variable associated with this checkbutton.

node_positions = {
    1: (1100, 450),
    2: (1000, 680),
    3: (820, 240),
    4: (700, 530),
    5: (550, 550),
    6: (350, 350),
    7: (350, 570),
}

node_assets = {
    1: ["WKK", "Gas boiler"],
    2: ["Gas boiler 1","Gas boiler 2","Gas boiler 3"],
    3: ["WKK"],
    4: ["None"],
    5: ["None"],
    6: ["Gas boilers"],
    7: ["WKK", "Gas boiler"],
}

checkbox_vars = {node: [] for node in node_assets}

for node, (x, y) in node_positions.items():
    y_offset = y  # Start with the original y position
    for asset in node_assets[node]:
        y_offset = create_checkbox(x, y_offset, asset, checkbox_vars, node)  # Update the y_offset for stacking

frame.mainloop()