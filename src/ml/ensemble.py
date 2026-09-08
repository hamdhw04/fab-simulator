import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
import matplotlib.pylab as plt

np.random.seed(42) #global seed

GB_PARAMETERS = {"max_depth": 3, "learning_rate": 0.1, "n_estimators": 100}
GB_N_BOOTSTRAP_MODELS = 30
tools = ["Epi","Oxidation","Photo","Etch","Diffusion","Metal Deposition"]

def build_ensemble(training_df, testing_df, n_bootstrapping_models:int = GB_N_BOOTSTRAP_MODELS, gb_parms: dict =  GB_PARAMETERS) -> list:
    models = []
    predictions = []
    final_means = []
    final_std = []
    for i in range(n_bootstrapping_models):
        resamples = training_df.sample(frac=1.0, replace=True)
        model = GradientBoostingRegressor(**gb_parms)
        model.fit(resamples[["Input 1", "Input 2"]], resamples["RUL"])
        models.append(model)        
    for model in models:
        predictions.append(model.predict(testing_df[["Input 1","Input 2"]]))
    ensemble_metrics = pd.DataFrame(predictions)
    final_means.append(ensemble_metrics.mean())
    final_std.append(ensemble_metrics.std())
    return final_means, final_std, 

comparisons = {}

for tool in tools:

    average_std = []

    train_data = pd.read_csv(f"data/processed/{tool}_training.csv")
    testing_data = pd.read_csv(f"data/processed/{tool}_test.csv")

    means, std = build_ensemble(train_data,testing_data)
    compare = testing_data
    means[0].name = "Predicted RUL Mean"
    std[0].name = "Predicted RUL Std"
    compare = pd.concat([compare,means[0]],axis=1)
    compare = pd.concat([compare,std[0]],axis=1)
    compare_low = compare[compare["RUL"] < 5]
    compare_high = compare[(compare["RUL"] >= 5) & (compare["RUL"] < 16)]
    average_std.append(float(compare_low["Predicted RUL Std"].mean()))
    average_std.append(float(compare_high["Predicted RUL Std"].mean()))
    comparisons[f"{tool}"] = average_std

print(comparisons)

