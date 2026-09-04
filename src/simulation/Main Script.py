import simpy
import numpy as np
from basemachine import SensorSpec, BaseMachine , Output
from toolgroup import ToolGroup
import random
import pandas as pd
from dataclasses import dataclass

@dataclass
class FactoryStats:
    profit : float = 0.0
    complete_lots : float = 0.0
    scrapped_lots : float = 0.0

def factory(interval:float,recipes:dict, final_data:list, stats): #interval is how often lot's come into the fab
    lotid = 0
    while True:
        yield env.timeout(np.random.exponential(interval))
        recipe = random.choice(list(recipes.values()))
        lotid += 1
        env.process(processing(recipe,lotid,final_data,stats))

def processing(recipe,id,final_data:list,stats):
    for i , group in enumerate(recipe):
        group_run = env.process(group.grouprun(id,final_data))
        yield group_run #hold until the process has completed, then move onto next element
        _ , failed = group_run.value
        if failed == True:
            stats.profit -= 500 + 500*(i+1) #each stage costs 500, lot not worked on costs 500
            stats.scrapped_lots += 1
            break
        if i+1 == len(recipe): #end of recipe
            stats.profit += (1+(i+1)*0.1)*2000 
            stats.complete_lots += 1

#Temperature, Growth Rate and Pressure. Will assume atmospheric pressure CVD, using trichlorosilane
epi_sensors = [
    SensorSpec(operating=1125, max=1200, aggression=10, positive=True), #temp
    SensorSpec(operating=101325, max=95000, aggression=4, positive= False) #pressure (pa)
]

ox_sensors = [
    SensorSpec(operating=1000, max=1250, aggression=15, positive=True), #temp
    SensorSpec(operating=65, max=80, aggression=5, positive= True) #o2 flow rate
]

photo_sensors = [
    SensorSpec(operating=100, max=140, aggression=8, positive=True), #exposure intensity
    SensorSpec(operating=4, max=6, aggression=2, positive= True) #alignment offset
]

etch_sensors = [
    SensorSpec(operating=100, max=200, aggression=16, positive=True),
    SensorSpec(operating=2, max=6, aggression=3, positive= True) 
]

diff_sensors = [
    SensorSpec(operating=1000, max=1400, aggression=8, positive=True),
    SensorSpec(operating=50, max=80, aggression=3, positive= True) 
]

mdep_sensors = [
    SensorSpec(operating=1400, max=1000, aggression=10, positive=False),
    SensorSpec(operating=1, max=6, aggression=12, positive= True) 
]


epi_output = Output(optimal = 3, bound = 1)
ox_output = Output(optimal = 5, bound = 2)
photo_output = Output(optimal = 5, bound = 10)
etch_output = Output(optimal = 3, bound = 1)
diff_output = Output(optimal = 0.5, bound = 2)
mdep_output = Output(optimal = 5, bound = 3)


env = simpy.Environment()
res = simpy.Resource(env, capacity=1)
SIM_RUNTIME = 1576800 #3 years - training data

epi = ToolGroup(env,"Epi",epi_sensors,epi_output,30,1.67,3)
ox = ToolGroup(env, "Oxidation",ox_sensors,ox_output,255,25,5)
photo = ToolGroup(env,"Photo",photo_sensors,photo_output,5.5,0.5,2)
etch = ToolGroup(env, "Etch",etch_sensors,etch_output,60,3.33,3)
diff = ToolGroup(env, "Diffusion",diff_sensors,diff_output,480,80,3)
mdep = ToolGroup(env, "Metal Deposition",mdep_sensors,mdep_output,100,16.67,2)

tools = ["Epi","Oxidation","Photo","Etch","Diffusion","Metal Deposition"]

recipes = {'recipe1' : [epi,ox,photo,etch,mdep],
           'recipe2' : [epi,ox,photo,etch,diff,photo,etch,mdep],
            'recipe3' : [epi,ox,photo,etch,ox,photo,etch,mdep],
            'recipe4' : [epi,ox,photo,etch,ox,photo,etch,diff,photo,etch,mdep],
            'recipe5' : [epi,ox,photo,etch,diff,photo,etch,diff,photo,etch,mdep]
           }

final = []
stats = FactoryStats()
factory = env.process(factory(100, recipes,final,stats))

factory
env.run(until=SIM_RUNTIME)

simulation_data = pd.DataFrame(final)
for i,tool in enumerate(tools):
    data = simulation_data[(simulation_data["Tool Group"] == tool)]
    data.to_csv(f"data/raw/{tool}.csv", index=False)