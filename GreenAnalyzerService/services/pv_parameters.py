import optuna
import pandas as pd
import services.modeler

import numpy as np
import math

def eval_metric(y_true, y_pred) :
#     res = 2 * abs(y_true - y_pred) / (y_true + y_pred)
#     res = res.fillna(0)
#     #res[res == 2] = 0
#     return res.mean()*100
    return 2 * 100 * np.mean((np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred))).map(lambda x: 0 if math.isnan(x) else x))

def find_params(df, pv_col, panel_tilt, panel_size, n_trials=100) :
    
    def _(doc):
        return doc

    def objective(trial):
    
        performance_ratio = trial.suggest_float('performance_ratio', 70, 100) # = 79.26 # (%)
        system_losses = trial.suggest_float('system_losses', 5, 20) # = 12 # (%) around x% (10.7+3.6, 10.7+2.7, 5.9+3.6)
    
        g = trial.suggest_int('g', -180, 180)
    
        nameplate = trial.suggest_float('nameplate', 0.80, 1.05)
        inverter_transformer = trial.suggest_float('inverter_transformer', 0.88, 0.98)
        mismatch = trial.suggest_float('mismatch', 0.97, 0.995)
        connections = trial.suggest_float('connections', 0.99, 0.997)
        dc_wiring = trial.suggest_float('dc_wiring', 0.97, 0.99)
        ac_wiring = trial.suggest_float('ac_wiring', 0.98, 0.993)
        soiling = trial.suggest_float('soiling', 0.30, 0.995)
        availability = trial.suggest_float('availability', 0, 0.995)
        shading = trial.suggest_float('shading', 0, 1)
        sun_tracking = trial.suggest_float('sun_tracking', 0.95, 1)
        age = trial.suggest_float('age', 0.70, 1)
    
        df['energy'] = df.apply(lambda x: services.modeler.MathModel().calculate_energy(x['direct_normal_irradiance'], 
                                                       x['diffuse_radiation'], x['shortwave_radiation'], 
                                                       x['zenith'], x['azimuth'], x['temperature_2m'],
                                                       panel_size, panel_tilt,
                                                       performance_ratio=performance_ratio, 
                                                       system_losses=system_losses, g=g,
                                                       nameplate=nameplate, inverter_transformer=inverter_transformer,
                                                       mismatch=mismatch, connections=connections, dc_wiring=dc_wiring,
                                                       ac_wiring=ac_wiring, soiling=soiling, availability=availability,
                                                       shading=shading, sun_tracking=sun_tracking, age=age), axis=1)

        score = eval_metric(df[pv_col],df['energy'])

        return score

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials, n_jobs = -1, show_progress_bar=True)

    print("Best trial:")
    best_trial = study.best_trial
    print("  Value: ", best_trial.value)
    print("  Params: ")
    for key, value in best_trial.params.items():
        print("    {}: {}".format(key, value))
        
    return best_trial.params