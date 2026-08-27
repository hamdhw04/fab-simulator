import simpy
import numpy as np
from basemachine import SensorSpec, BaseMachine , Output
from toolgroup import ToolGroup
import random
import pandas as pd
import json
import matplotlib.pyplot

def factory(interval:float,recipes:dict, final_data:list): #interval is how often lot's come into the fab
    lotid = 0
    while True:
        yield env.timeout(np.random.exponential(interval))
        recipe = random.choice(list(recipes.values()))
        lotid += 1
        env.process(processing(recipe,lotid,final_data))
        print(f"lot{lotid} started.")

def processing(recipe,id,final_data:list):
    for group in recipe:
        group_run = env.process(group.grouprun(id,final_data))
        yield group_run #hold until the process has completed, then move onto next element
        results_dict = group_run.value
   

#Temperature, Growth Rate and Pressure. Will assume atmospheric pressure CVD, using trichlorosilane
epi_sensors = [
    SensorSpec(name="temperature", unit="°C", operating=1125, max=1200, aggression=10, positive=True), 
    SensorSpec(name="pressure", unit="Pa", operating=101325, max=95000, aggression=4, positive= False)
]

ox_sensors = [
    SensorSpec(name="temperature", unit="°C", operating=1000, max=1250, aggression=15, positive=True), 
    SensorSpec(name="o2 flow rate", unit="cm3/min", operating=65, max=80, aggression=5, positive= True)
]

photo_sensors = [
    SensorSpec(name="exposure intensity", unit="mJ/cm2", operating=100, max=140, aggression=8, positive=True), 
    SensorSpec(name="alignment offset", unit="nm", operating=4, max=6, aggression=2, positive= True)
]

epi_output = Output(optimal = 3, bound = 1)
ox_output = Output(optimal = 5, bound = 2)
photo_output = Output(optimal = 400, bound = 200)

env = simpy.Environment()
res = simpy.Resource(env, capacity=1)

SIM_RUNTIME = 10000
epi = ToolGroup(env,"Epi",epi_sensors,epi_output,30,1.67,3)
ox = ToolGroup(env, "Oxidation",ox_sensors,ox_output,255,25,5)
photo = ToolGroup(env,"Photo",photo_sensors,photo_output,5.5,0.5,2)

recipes = {'recipe1' : [epi,ox,photo],
           'recipe2' : [epi,ox,photo,ox],
            'recipe3' : [epi,ox]
           }

final = []
env.process(factory(100, recipes,final))

env.run(until=SIM_RUNTIME)

test = pd.DataFrame(final)
test.to_csv("test.csv")
epi = test[test['Tool Group'] == "Epi"]
epi.to_csv("epitest.csv")

