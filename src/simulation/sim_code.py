import simpy
import numpy as np
from toolgroup import ToolGroup
import pandas as pd
from dataclasses import dataclass

models_on = True

@dataclass
class FactoryStats:
    profit : float = 0.0
    complete_lots : float = 0.0
    scrapped_lots : float = 0.0
    prevented : float = 0.0

def factory(env, interval:float,recipes:dict, final_data:list, stats,rng): #interval is how often lot's come into the fab
    lotid = 0
    while True:
        yield env.timeout(rng.exponential(interval))
        chosen_key = rng.choice(list(recipes.keys()))
        recipe = recipes[chosen_key]
        lotid += 1
        env.process(processing(env,recipe,lotid,final_data,stats))

def processing(env,recipe,id,final_data:list,stats):
    for i , group in enumerate(recipe):
        group_run = env.process(group.grouprun(id,final_data))
        yield group_run #hold until the process has completed, then move onto next element
        _ , failed, prevent = group_run.value
        if failed == True:
            stats.profit -= 1000 + 200 + 200*(i+1) #each stage costs 500, lot not worked on costs 500, tool repair costs 1000
            stats.scrapped_lots += 1
            break
        if prevent == True:
            stats.profit -= 500 #less cost to repair a tool before breakdown
            stats.prevented += 1
        if i+1 == len(recipe): #end of recipe
            stats.profit += (1+(i+1)*0.1)*2000 
            stats.complete_lots += 1




