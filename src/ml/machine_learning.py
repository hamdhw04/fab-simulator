import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

tools = ["Epi","Oxidation","Photo","Etch","Diffusion","Metal Deposition"]

def learning(tools:list,model,mode:int) -> dict:
    results = {}
    for tool in tools:
        training_data = pd.read_csv(f"data/processed/{tool}_training.csv")
        test_data = pd.read_csv(f"data/processed/{tool}_test.csv")


        if mode == 1:
            features = ["Input 1","Input 2","Rolling Mean 1","Rolling Mean 2"]
        elif mode == 2:
            features =  ["Input 1","Input 2"]
        elif mode == 3 : 
            features = ["Rolling Mean 1","Rolling Mean 2"]

        target = "RUL"

        x_train,y_train = training_data[features], training_data[target]
        x_test,y_test = test_data[features], test_data[target]

        model.fit(x_train,y_train)

        predictions = model.predict(x_test)

        mask_low = y_test < 5 #binning to see errors near RUL = 0, which is more critical 
        mask_high = ~mask_low

        mae_low = mean_absolute_error(y_test[mask_low], predictions[mask_low])
        mae_high = mean_absolute_error(y_test[mask_high], predictions[mask_high])

        rmse_low = root_mean_squared_error(y_test[mask_low], predictions[mask_low])
        rmse_high = root_mean_squared_error(y_test[mask_high], predictions[mask_high])

        # errors = pd.DataFrame({
        # "true_rul": y_test.values,
        # "predicted_rul": predictions,
        # "abs_error": abs(y_test.values - predictions)
        # })

        # worst_predictions = errors.sort_values("abs_error", ascending=False).head(20)
        # print(worst_predictions)

        results[tool] = {"mae_low": mae_low, "mae_high": mae_high, "rmse_low" : rmse_low, "rmse_high": rmse_high}

    return results

modes = [1,2,3]

for test in modes:
    if test == 1:
        features = "ALL"
    elif test == 2:
        features =  "RAW"
    elif test == 3 : 
        features = "ROLLED"
    rf_results = pd.DataFrame(learning(tools, RandomForestRegressor(n_estimators=300, random_state=42),test)).T
    gb_results = pd.DataFrame(learning(tools, GradientBoostingRegressor(max_depth=3, learning_rate=0.1, random_state=42),test)).T
    rf_results = rf_results.round(2)
    gb_results = gb_results.round(2)
    with pd.ExcelWriter('model_comparisons.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        rf_results.to_excel(writer, sheet_name=f'rf_{features}', index=False)
        gb_results.to_excel(writer, sheet_name=f'gb_{features}', index=False)


