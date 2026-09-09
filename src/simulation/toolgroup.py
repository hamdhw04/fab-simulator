from dataclasses import dataclass
from basemachine import BaseMachine, SensorSpec, Output
import simpy
import joblib
import hashlib

def stable_seed(*parts) -> int: #handles unique seed creation for BaseMachine objects, hash is unique per run, whilst .md5 is not.
    combined = "-".join(str(p) for p in parts)          # e.g. "42-Epi-0"
    digest = hashlib.md5(combined.encode()).hexdigest()   # deterministic hex string
    return int(digest, 16) % (2**32)                       # convert to int, keep it in a sane range

@dataclass
class ToolGroup():
    env : simpy.Environment
    tool_name : str
    sensors: list[SensorSpec]
    output_spec : Output
    pr_mean : float
    pr_std : float
    num_tools : int #amount of tools in a group
    models_on : bool
    seeds: int

    def __post_init__(self):
        self.tools= [
            BaseMachine(self.env,self.tool_name,self.sensors,self.output_spec,self.pr_mean,self.pr_std,i,model_on=self.models_on,seed=abs(stable_seed(self.seeds,self.tool_name,i)))
            for i in range(self.num_tools)
        ] #creating n different instances of BaseMachine so all experience unique drift 

        if self.models_on == True:
            self.models = joblib.load(f"src/ml/models/{self.tool_name}_ensemble.pkl")
        else:
            self.models = []
        self.resources = [simpy.Resource(self.env,capacity=1) for i in range(self.num_tools)] #array of simpy resources for each machine

    def grouprun(self,id,simdata:list):
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

        tool_run = self.env.process(self.tools[tool_index].running(id,simdata,self.models))
        yield tool_run
        self.resources[tool_index].release(granted)
        return tool_run.value

    

                



