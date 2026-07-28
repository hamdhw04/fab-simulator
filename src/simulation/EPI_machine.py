import simpy
import numpy as np

SIM_RUNTIME = 600

def epi_machine(env : simpy.Environment):
    """Simulates a single EPI tool processing wafers. 
    Three parameters - Temperature, Growth Rate and Pressure
    Will assume atmospheric pressure CVD
    Using trichlorosilane

    Args:
        env: SimPy Environment driving the simulation
    """

    rng = np.random.default_rng()

    pr_time_mean = 30
    pr_time_stdev = 1.67 #for 99.7% of data points to fall between 20-35 minutes

    tool_temp_mean = 1125
    tool_temp_stdev = 25 #for 99.7% of data points to fall between 1050 and 1200 degrees C

    tool_pres_mean = 101325
    tool_pres_stdev = 30 #shouldn't see strong deviation

    growth_rate_mean = 3.5
    growth_rate_stdev = 0.5 #for 99.7% of data points to fall between 2 and 5 um/min
    print(f"\nLot entered tool at {int(env.now)}")
    process_duration = rng.normal(loc = pr_time_mean, scale = pr_time_stdev)
    yield env.timeout(process_duration)

    tool_temp = rng.normal(loc = tool_temp_mean, scale = tool_temp_stdev)
    tool_pres = rng.normal(loc = tool_pres_mean, scale = tool_pres_stdev)
    growth = rng.normal(loc = growth_rate_mean, scale = growth_rate_stdev)
    print(f"Lot tracked out of tool at {int(env.now)}")
    print(f"Machine Temperature = {int(tool_temp)}°C")
    print(f"Machine Pressure = {int(tool_pres)}Pa")
    print(f"Epitaxial Growth Rate = {growth:.1f}um/min")

def epi_machine2(env : simpy.Environment):
    """Simulates a single EPI tool processing wafers. 
    Three parameters - Temperature, Growth Rate and Pressure
    Will assume atmospheric pressure CVD
    Using trichlorosilane

    Args:
        env: SimPy Environment driving the simulation
    """

    rng = np.random.default_rng()

    pr_time_mean = 30
    pr_time_stdev = 1.67 #for 99.7% of data points to fall between 20-35 minutes

    tool_temp_mean = 1125
    tool_temp_stdev = 25 #for 99.7% of data points to fall between 1050 and 1200 degrees C

    tool_pres_mean = 101325
    tool_pres_stdev = 30 #shouldn't see strong deviation

    growth_rate_mean = 3.5
    growth_rate_stdev = 0.5 #for 99.7% of data points to fall between 2 and 5 um/min
    print(f"\nLot entered tool at {int(env.now)}")
    process_duration = rng.normal(loc = pr_time_mean, scale = pr_time_stdev)
    yield env.timeout(process_duration)

    tool_temp = rng.normal(loc = tool_temp_mean, scale = tool_temp_stdev)
    tool_pres = rng.normal(loc = tool_pres_mean, scale = tool_pres_stdev)
    growth = rng.normal(loc = growth_rate_mean, scale = growth_rate_stdev)
    print(f"Lot tracked out of tool 2 at {int(env.now)}")
    print(f"Machine Temperature = {int(tool_temp)}°C")
    print(f"Machine Pressure = {int(tool_pres)}Pa")
    print(f"Epitaxial Growth Rate = {growth:.1f}um/min")

def processing(recipe):
    for machine in recipe:
        yield env.process(machine(env))

recipe = [epi_machine,epi_machine2]

env = simpy.Environment()

env.process(processing(recipe))

env.run(until=SIM_RUNTIME)



