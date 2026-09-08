import pandas as pd
import numpy as np

def conversion(df):
    df["Shifted"] = df["Failed"].shift(periods=1, fill_value= False)
    df["Cycle Group"] = df["Shifted"].cumsum()
    df["Forward"] = df.groupby(["Cycle Group"]).cumcount()
    df["Cycle Size"] = df.groupby("Cycle Group")["Failed"].transform("size")
    df["RUL"] = df["Cycle Size"] - df["Forward"] - 1

    df["Shifted"] = df.groupby("Tool ID")["Failed"].shift(periods=1, fill_value=False)
    df["Cycle Group"] = df.groupby("Tool ID")["Shifted"].cumsum()
    df["Cycle ID"] = df["Tool ID"].astype(str) + "_" + df["Cycle Group"].astype(str) #avoiding the same cycle numbers across different tool instances

    df["Forward"] = df.groupby("Cycle ID").cumcount() 
    df["Cycle Size"] = df.groupby("Cycle ID")["Failed"].transform("size")
    df["RUL"] = df["Cycle Size"] - df["Forward"] - 1

    last_cycle_per_instance = df.groupby("Tool ID")["Cycle Group"].transform("max")
    is_last_cycle = df["Cycle Group"] == last_cycle_per_instance #cycle group as a series of boolean values
    # drop only instances whose OWN last cycle never breached
    incomplete_final_cycle = is_last_cycle & ~df.groupby("Cycle ID")["Failed"].transform("any") #NO BREACH
    df = df[~incomplete_final_cycle] #drop every row where incomplete final cycle is true

    df["Rolling Mean 1"] = df.groupby("Cycle ID")["Input 1"].rolling(5).mean().reset_index(level=0, drop=True)
    df["Rolling Mean 2"] = df.groupby("Cycle ID")["Input 2"].rolling(5).mean().reset_index(level=0, drop=True)

    df = df.dropna(subset=["Rolling Mean 1", "Rolling Mean 2"]) #RUL calculations have NaN's during early cycle, does not influence near breach RUL so will be omitted

    instances = df['Tool ID'].unique() #shuffling tool ID's to see what is used as test data and what is used as training data
    rng = np.random.default_rng(seed=42)
    rng.shuffle(instances)

    split_point = int(0.7 * len(instances))
    train_instances, test_instances = instances[:split_point], instances[split_point:]

    train_df = df[df['Tool ID'].isin(train_instances)]
    test_df = df[df['Tool ID'].isin(test_instances)]

    train_df = train_df[['Input 1','Input 2', 'Rolling Mean 1', 'Rolling Mean 2', 'RUL']]
    test_df = test_df[['Input 1','Input 2', 'Rolling Mean 1', 'Rolling Mean 2', 'RUL']]

    return train_df, test_df

tools = ["Epi","Oxidation","Photo","Etch","Diffusion","Metal Deposition"]

for i,tool in enumerate(tools):
    data = pd.read_csv(f"data/raw/{tool}.csv")
    training,test = conversion(data)
    training.to_csv(f"data/processed/{tool}_training.csv", index=False)
    test.to_csv(f"data/processed/{tool}_test.csv", index=False)

