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

    def running(self,id,simdata:list):

        rng = np.random.default_rng() #each machine has it's own randomness

        data = {}
        data["Tool Group"] = self.tool_name
        data["Tool ID"] = self.index
        data["LotID"] = id

        data["Time In"] = int(self.env.now)
        # print(f"\nLot{id} entered {self.tool_name} at {int(self.env.now)}")
        process_duration = rng.normal(loc = self.pr_mean, scale = self.pr_std)
        yield self.env.timeout(process_duration)

        data["Time Out"] = int(self.env.now)
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


            self.distances[i] = sign *(self.reading[i] - self.baseline[i]) #current distance from optimal output

        data["Input 1"] = self.reading[0]
        data["Input 2"] = self.reading[1]

        new_output = self.kconst*(self.distances[0] + (self.distances[1]**2) + (0.5*(self.distances[0]*self.distances[1]))) + self.cconst
        data["Output"] = new_output

        self.failed = False

        if new_output * self.output_sign > self.output_sign * self.bound:
            print(f"Wafer out of spec, Tool #{self.index} failure, repairing")
            self.failed = True
            data["Failed"] = self.failed
            yield self.env.timeout(100)
            self.reading = [sensor.operating for sensor in self.sensors]
            self.distances = [0,0]
        else:
            data["Failed"] = self.failed

        simdata.append(data)

        return simdata
        

