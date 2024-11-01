# Libraries

import pandas as pd
import numpy as np
import datetime

from pycaret.regression import *

import warnings

warnings.simplefilter('ignore')

df = pd.read_csv('data_november23_february24_openmeteo-hour.csv', index_col='datetime', parse_dates=True, infer_datetime_format=True)



df = df.reset_index()
df = df.sort_values(by='datetime')
df['month'] = df['datetime'].dt.month
df['hour'] = df['datetime'].dt.hour
df = df.set_index('datetime')
df = df.drop(['error1','error2','error3','time'],axis=1)
df = df.fillna(0)


target = 'inverter1'
extra_feature = 'energy1'


def generate_model(df, target = 'inverter1',features=features, end=end):

    # Training/Validate slit
    data = df[[target]+features].reset_index()

    data_train = data.loc[data['datetime'] < end]
    data_train = data_train.set_index('datetime')
    data_train = data_train
    data_test = data.loc[data['datetime'] >= end]
    data_test = data_test.set_index('datetime')
    
    X_test = data_test[features]
    y_test = data_test[target]
    
    # Model Setup
    s = setup(data = data_train, target = target, session_id=123, fold=5)

    best1 = s.compare_models(include = ['rf', 'et', 'gbr', 'br', 'xgboost', 'dt', 'ada'])

    # best1 = stack_models(best1)
    best1 = tune_model(best1, n_iter = 40, choose_better = True)
    
    return best1, X_test, y_test
    
    

end = '2024-01-01 23:00:00' #26/1, 2/2, 7/2
end_train = '2024-01-01 23:00:00'

model, validate_X, validate_y = generate_model(df, target = target, end=end)

p = pd.DataFrame({'pred': model.predict(validate_X[model.feature_names_in_])})
p[target] = validate_y.reset_index()[target]

t = (abs(p[target] - p['pred'])) / ((p[target] + p['pred'])/2)
t = t.fillna(0)
t[t==1]=0
t.mean()