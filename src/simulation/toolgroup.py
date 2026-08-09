from dataclasses import dataclass
from basemachine import BaseMachine, SensorSpec, Output
import simpy

@dataclass
class ToolGroup():
    env : simpy.Environment
    tool_name : str
    sensors: list[SensorSpec]
    output_spec : Output
    pr_mean : float
    pr_std : float
    num_tools : int #amount of tools in a group

    def __post_init__(self):
        self.tools= [
            BaseMachine(self.env,self.tool_name,self.sensors,self.output_spec,self.pr_mean,self.pr_std,i)
            for i in range(self.num_tools)
        ] #creating n different instances of BaseMachine so all experience unique drift 

        self.resources = [simpy.Resource(self.env,capacity=1) for i in range(self.num_tools)] #array of simpy resources for each machine

    def grouprun(self):
        requests = [resource.request() for resource in self.resources] #all requests for tools
        result = yield simpy.AnyOf(self.env,requests)
        granted = list(result.keys())[0] #resource that was granted, [0] just in case multiple resources become free at the same instance
        tool_index = requests.index(granted) #tool lot is going to

        for r in requests:
            if r is granted:
                continue
            elif r in result:
                self.resources[requests.index(r)].release(r)
            else:
                r.cancel()

        tool_run = self.env.process(self.tools[tool_index].running())
        yield tool_run
        self.resources[tool_index].release(granted)
        return tool_run.value

    

                



