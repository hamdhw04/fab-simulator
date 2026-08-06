import simpy
import numpy as np
from dataclasses import dataclass, field
from typing import List


env = simpy.Environment()

@dataclass
class SensorSpec:
    name : str
    unit : str
    operating : float
    max : float
    aggression : float #between 1-10, 10 being aggressive degradation
    positive : bool #positive trend or not

@dataclass
class Output:
    optimal : float
    lower_bound : float
    upper_bound : float

@dataclass
class BaseMachine:
    env : simpy.Environment
    tool_name : str
    sensors: list[SensorSpec]
    output_spec : Output
    pr_mean : float
    pr_std : float
    optimal : float = 0.0
    lower : float = 0.0
    upper : float = 0.0

    # reading: List[bool] = field(init=False)

    def __post_init__(self):
        self.reading = [sensor.operating for sensor in self.sensors] #intial readings, will mutate this
        self.optimal = self.output_spec.optimal
        self.lower = self.output_spec.lower_bound
        self.upper = self.output_spec.upper_bound

        self.const = self.optimal / (self.reading[0] + (self.reading[1]**2) + (0.5*(self.reading[0]*self.reading[1]))) #scaling constant to get to correct output scale, alpha = beta = 1, gamma = 0.5 (interaction) in non-linear relationship.

    def running(self,id,reading:list,k:float):
        rng = np.random.default_rng() #each machine has it's own randomness

        data = {}
        data[self.tool_name] = []

        data[self.tool_name].append(int(self.env.now))
        # print(f"\nLot{id} entered {self.tool_name} at {int(self.env.now)}")
        process_duration = rng.normal(loc = self.pr_mean, scale = self.pr_std)
        yield self.env.timeout(process_duration)

        data[self.tool_name].append(int(self.env.now))
        # print(f"Lot{id} tracked out of {self.tool_name} at {int(self.env.now)}")

        for i,sensor in enumerate(self.sensors): #separating into index and items

            if sensor.positive == False:
                sign = -1
            else:
                sign = 1

            drift = sign* np.random.default_rng().exponential(1) #drift modelled as exponential distribution (positive values, no "healing")    
            noise = np.random.default_rng().normal(loc=0,scale=1) #noise modelled as normal distribution
            reading[i] = reading[i] + (sensor.aggression * drift) + noise

            print(f"{sensor.name} = {reading[i]:.1f}{sensor.unit}")
            data[self.tool_name].append(f"{reading[i]:.1f}{sensor.unit}")

        new_output = (k*reading[0]) + (k*(self.reading[1]**2)) + (k*0.5*(self.reading[0]*self.reading[1]))
        data[self.tool_name].append(new_output)

        if new_output > self.upper or new_output < self.lower:
            print("Tool failure, repairing")
            yield self.env.timeout(100)
            reading = [sensor.operating for sensor in self.sensors]

        return data
            

       
