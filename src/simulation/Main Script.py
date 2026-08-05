import simpy
import numpy as np
from basemachine import SensorSpec, BaseMachine
import random
import pandas
import json

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
        machine_run = env.process(machine.processing(id))
        yield machine_run #hold until the process has completed, then move onto next element
        results_dict[id].update(machine_run.value)
    final_data.update(results_dict)

#Temperature, Growth Rate and Pressure. Will assume atmospheric pressure CVD, using trichlorosilane
epi_sensors = [
    SensorSpec(name="temperature", unit="°C", mean=1125, std=25), #for 99.7% of data points to fall between 1050 and 1200 degrees C
    SensorSpec(name="pressure", unit="Pa", mean=101325, std=30), #shouldn't see strong deviation
    SensorSpec(name="growth_rate", unit="um/min", mean=3.5, std=0.5), #for 99.7% of data points to fall between 2 and 5 um/min
]

#Temperature, O2 Flow Rate and Time, will assume a target thickness of 100nm. constant temp.
ox_sensors = [
    SensorSpec(name="temperature", unit="°C", mean=1100, std=0),
    SensorSpec(name="o2 flow rate", unit="cm3/min", mean=3000, std=666.67), #for 99.7% of data to fall between 1000-5000 cm3/min
    SensorSpec(name="time", unit="min", mean=75, std=6.67), #for 99.7% of data to fall between 65-85 minutes
]

photo_sensors = [
    SensorSpec(name="exposure intensity", unit="mJ/cm2", mean=125, std=25), #50-200
    SensorSpec(name="alignment offset", unit="nm", mean=4.75, std=3.167), #0.5-10
    SensorSpec(name="Relative Humidity", unit="%RH", mean=42.5, std=0.833), #for 99.7% of data to fall between 65-85 minutes
]

env = simpy.Environment()

SIM_RUNTIME = 5000

epi = BaseMachine(env,"Epi",epi_sensors,30,1.67)
ox = BaseMachine(env,"Ox",ox_sensors,255,25) #3-5.5 hours including ramp up and ramp down
photo = BaseMachine(env,"Photo",photo_sensors,5.5,0.5) #4-7 minutes 

recipes = {'recipe1' : [epi,ox,photo],
           'recipe2' : [epi,ox,photo,ox]}

final = {}
env.process(factory(1000, recipes,final))

env.run(until=SIM_RUNTIME)
print(json.dumps(final,indent= 4))

