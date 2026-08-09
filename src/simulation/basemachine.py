import simpy
import numpy as np
from dataclasses import dataclass

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
    bound : float

@dataclass
class BaseMachine:
    env : simpy.Environment
    tool_name : str
    sensors: list[SensorSpec]
    output_spec : Output
    pr_mean : float
    pr_std : float
    index : int 
    optimal : float = 0.0
    bound : float = 0.0
    dmax : float = 0.0
    failed : bool = False
    

    # reading: List[bool] = field(init=False)

    def __post_init__(self):
        self.reading = [sensor.operating for sensor in self.sensors] #intial readings, will mutate this
        self.baseline = [sensor.operating for sensor in self.sensors] #used for constant calculations
        self.sensormax = [sensor.max for sensor in self.sensors] #max bounds for sensors
        self.sign = [sensor.positive for sensor in self.sensors] #signs

        self.max_distance = [] #intialising array for max distances for constant calculations
        self.distances = [0,0] #array to mutate distances in running function

        self.optimal = self.output_spec.optimal #optimal output 
        self.bound = self.output_spec.bound #value before output out of spec

        if self.optimal - self.bound > 0:
            self.output_sign = -1
        else:
            self.output_sign = 1

        for i,item in enumerate(self.sign):
            if self.sign[i] == True:
                self.dmax = -1 * (self.baseline[i] - self.sensormax[i])
                self.max_distance.append(self.dmax)
            else:
                self.dmax = (self.baseline[i] - self.sensormax[i]) #if output trend is downwards
                self.max_distance.append(self.dmax)

        #calculating constants for output non-linear relationship to inputs
        self.cconst = self.optimal
        self.kconst = (self.bound-self.optimal)/ (self.max_distance[0] + (self.max_distance[1]**2) + 0.5*(self.max_distance[0]*self.max_distance[1]))

    def running(self):

        rng = np.random.default_rng() #each machine has it's own randomness

        data = {}
        data[self.tool_name] = []

        data[self.tool_name].append(int(self.env.now))
        # print(f"\nLot{id} entered {self.tool_name} at {int(self.env.now)}")
        process_duration = rng.normal(loc = self.pr_mean, scale = self.pr_std)
        yield self.env.timeout(process_duration)

        data[self.tool_name].append(int(self.env.now))
        # print(f"Lot{id} tracked out of {self.tool_name} at {int(self.env.now)}")#

        for i,sensor in enumerate(self.sensors): #separating into index and items

            if sensor.positive == False:
                sign = -1
            else:
                sign = 1

            drift_mag = ((sensor.aggression/100)*self.max_distance[i])
            drift = sign* np.random.default_rng().exponential(scale = drift_mag) #drift modelled as exponential distribution (positive values, no "healing")    
            noise = np.random.default_rng().normal(loc=0,scale=1) #noise modelled as normal distribution
            self.reading[i] = self.reading[i] + drift + noise

            print(f"{sensor.name} = {self.reading[i]:.1f}{sensor.unit}")
            data[self.tool_name].append(f"{self.reading[i]:.1f}{sensor.unit}")

            self.distances[i] = sign *(self.reading[i] - self.baseline[i]) #current distance from optimal output

        new_output = self.kconst*(self.distances[0] + (self.distances[1]**2) + (0.5*(self.distances[0]*self.distances[1]))) + self.cconst
        data[self.tool_name].append(new_output)
        data[self.tool_name].append(self.index)

        self.failed = False

        if new_output * self.output_sign > self.output_sign * self.bound:
            print(f"Wafer out of spec, Tool #{self.index} failure, repairing")
            self.failed = True
            data[self.tool_name].append(self.failed)
            yield self.env.timeout(100)
            self.reading = [sensor.operating for sensor in self.sensors]
            self.distances = [0,0]
        else:
            data[self.tool_name].append(self.failed)

        return data
        

    
