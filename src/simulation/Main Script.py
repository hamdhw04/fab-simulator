import simpy
import numpy as np
from basemachine import SensorSpec , Output
from toolgroup import ToolGroup
import pandas as pd
from sim_code import FactoryStats, factory

def run_sim(seed:int,models_on:bool = False,sim_time:int):
    env = simpy.Environment()
    rng = np.random.default_rng(seed)

    epi = ToolGroup(env,"Epi",epi_sensors,epi_output,30,1.67,3,models_on=models_on,seeds=seed)
    ox = ToolGroup(env, "Oxidation",ox_sensors,ox_output,255,25,5,models_on=models_on,seeds=seed)
    photo = ToolGroup(env,"Photo",photo_sensors,photo_output,5.5,0.5,2,models_on=models_on,seeds=seed)
    etch = ToolGroup(env, "Etch",etch_sensors,etch_output,60,3.33,3,models_on=models_on,seeds=seed)
    diff = ToolGroup(env, "Diffusion",diff_sensors,diff_output,480,80,3,models_on=models_on,seeds=seed)
    mdep = ToolGroup(env, "Metal Deposition",mdep_sensors,mdep_output,100,16.67,2,models_on=models_on,seeds=seed)

    recipes = {'recipe1' : [epi,ox,photo,etch,mdep],
            'recipe2' : [epi,ox,photo,etch,diff,photo,etch,mdep],
                'recipe3' : [epi,ox,photo,etch,ox,photo,etch,mdep],
                'recipe4' : [epi,ox,photo,etch,ox,photo,etch,diff,photo,etch,mdep],
                'recipe5' : [epi,ox,photo,etch,diff,photo,etch,diff,photo,etch,mdep]
            }

    final = []
    stats = FactoryStats()
    simulate = env.process(factory(env,100, recipes,final,stats,rng))

    simulate
    env.run(until=sim_time)

    simulation_statistics = [models_on,stats.complete_lots,stats.scrapped_lots,stats.profit,stats.prevented]
    simulation_data = pd.DataFrame(final)

    simulation_statistics = pd.DataFrame({"Seed": [seed], "Models On": [models_on], "Completed Lots": [stats.complete_lots], "Scrapped Lots": [stats.scrapped_lots], "Profit Generated": [stats.profit], "Preventative Maintenance Events": [stats.prevented]})

    return simulation_data, simulation_statistics




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

# tools = ["Epi","Oxidation","Photo","Etch","Diffusion","Metal Deposition"]

models_on = True

final, stats = run_sim(seed=40,models_on=False,sim_time=5000)
print(stats)



