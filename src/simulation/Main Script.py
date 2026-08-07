import simpy
import numpy as np
from basemachine import SensorSpec, BaseMachine , Output
import random
import pandas
import json
import matplotlib.pyplot

def factory(interval:float,recipes:dict, final_data:dict): #interval is how often lot's come into the fab
    lotid = 0
    while True:
        yield env.timeout(np.random.exponential(interval))
        recipe = random.choice(list(recipes.values()))
        lotid += 1
        env.process(processing(recipe,lotid,final_data))
        print(f"lot{lotid} started.")

def processing(recipe,id,final_data:dict):
    results_dict = {}
    results_dict[id] = {}
    for machine in recipe:
        machine_run = env.process(machine.running(id))
        yield machine_run #hold until the process has completed, then move onto next element
        results_dict[id].update(machine_run.value)
    final_data.update(results_dict)

#Temperature, Growth Rate and Pressure. Will assume atmospheric pressure CVD, using trichlorosilane
epi_sensors = [
    SensorSpec(name="temperature", unit="°C", operating=1125, max=1200, aggression=10, positive=True), #for 99.7% of data points to fall between 1050 and 1200 degrees C
    SensorSpec(name="pressure", unit="Pa", operating=101325, max=95000, aggression=4, positive= False), #shouldn't see strong deviation
]

epi_output = Output(optimal = 3, bound = 1)
env = simpy.Environment()

SIM_RUNTIME = 5000

epi = BaseMachine(env,"Epi",epi_sensors,epi_output,30,1.67)

recipes = {'recipe1' : [epi]}

final = {}
env.process(factory(100, recipes,final))

env.run(until=SIM_RUNTIME)
print(json.dumps(final,indent= 4))


