import simpy
import numpy as np
from dataclasses import dataclass, field


env = simpy.Environment()

@dataclass
class SensorSpec:
    name : str
    unit : str
    mean : float
    std : float

@dataclass
class BaseMachine:
    env : simpy.Environment
    tool_name : str
    sensors: list[SensorSpec]
    pr_mean : float
    pr_std : float

    def processing(self,id):
        rng = np.random.default_rng() #each machine has it's own randomness

        data = {}
        data[self.tool_name] = []

        data[self.tool_name].append(int(self.env.now))
        print(f"\nLot{id} entered {self.tool_name} at {int(self.env.now)}")
        process_duration = rng.normal(loc = self.pr_mean, scale = self.pr_std)
        yield self.env.timeout(process_duration)

        data[self.tool_name].append(int(self.env.now))
        print(f"Lot{id} tracked out of {self.tool_name} at {int(self.env.now)}")

        for sensor in self.sensors:
            reading = rng.normal(loc = sensor.mean, scale = sensor.std)
            print(f"{sensor.name} = {reading:.1f}{sensor.unit}")
            data[self.tool_name].append(f"{reading:.1f}{sensor.unit}")

        return data
            

       
