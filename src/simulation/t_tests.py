from scipy import stats
import pandas as pd
import numpy as np

data = pd.read_csv("ab_results.csv")
model_on_profit = data[data["Models On"] == True]["Profit"].values.tolist()
model_off_profit = data[data["Models On"] == False]["Profit"].values.tolist()

pct_diff = [((on - off)/off) * 100 for on,off in zip(model_on_profit,model_off_profit)]
mean_pct = np.mean(pct_diff)
ci_low  = np.quantile(pct_diff,0.025)
ci_high = np.quantile(pct_diff,0.975)
print(pct_diff)
print(mean_pct)
print(ci_low)
print(ci_high)

t_stat, p_value = stats.ttest_rel(model_on_profit, model_off_profit)
print(t_stat)
print(p_value)

