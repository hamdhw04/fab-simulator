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

    def processing(self):
        rng = np.random.default_rng() #each machine has it's own randomness
        
        print(f"\nLot entered tool at {int(self.env.now)}")
        process_duration = rng.normal(loc = self.pr_mean, scale = self.pr_std)
        yield self.env.timeout(process_duration)

        print(f"Lot tracked out of tool at {int(self.env.now)}")

        for sensor in self.sensors:
            reading = rng.normal(loc = sensor.mean, scale = sensor.std)
            print(f"{sensor.name} = {reading:.1f}{sensor.unit}")
                
    