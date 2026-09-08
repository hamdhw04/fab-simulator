import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
import matplotlib.pylab as plt

GB_PARAMETERS = {"max_depth": 3, "learning_rate": 0.1, "n_estimators": 100}
tools = ["Epi","Oxidation","Photo","Etch","Diffusion","Metal Deposition"]

def build_ensemble(training_df, testing_df, n_bootstrapping_models:int, gb_parms: dict =  GB_PARAMETERS) -> list:
    models = []
    n_values = []
    final_means = []
    final_std = []
    avg_std = []
    for i in range(n_bootstrapping_models):
        resamples = training_df.sample(frac=1.0, replace=True)
        model = GradientBoostingRegressor(**gb_parms)
        model.fit(resamples[["Input 1", "Input 2"]], resamples["RUL"])
        models.append(model)
    for k in range(int(n_bootstrapping_models/5)+1):
        constant = 5*k
        n_values.append(constant)
        predictions = []
        for j in range(constant):
            predictions.append(models[j].predict(testing_df[["Input 1","Input 2"]]))
        ensemble_metrics = pd.DataFrame(predictions)
        final_means.append(ensemble_metrics.mean())
        final_std.append(ensemble_metrics.std())
    avg_std = [s.mean() for s in final_std]
    return final_means, final_std, avg_std, n_values

train_data = pd.read_csv(f"data/processed/Epi_training.csv")
testing_data = pd.read_csv(f"data/processed/Epi_test.csv")

_,_,avg,n = build_ensemble(train_data,testing_data,50)

plt.figure(figsize=(20, 5))
plt.plot(n,avg)
plt.title("Bootstrapping Std Stability with Increasing Bootstrapped GB Regressors")
plt.xlabel("Number of GB Regressors")
plt.ylabel("Average Std")
plt.grid(True)
plt.ylim(0.15, 0.20)
plt.savefig("notebooks/convergence_graph.png")
plt.show()
