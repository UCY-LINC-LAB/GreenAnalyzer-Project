import pandas as pd
from datetime import datetime, timedelta
import pytz

import numpy as np
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from sklearn.ensemble import RandomForestRegressor
from skforecast.utils import save_forecaster
from lightgbm import LGBMRegressor
import math

# from services.cyprus_energy_mix_service import get_cy_hist_energy_mix_data
# from services.weather import WeatherService
from cyprus_energy_mix_service import get_cy_hist_energy_mix_data
from weather import WeatherService


def update_mix_cyprus():

    df = pd.read_csv('EnergyMix_CY_historical_estimated.csv', index_col='timestamp', parse_dates=True)
    df = df.reset_index()
    
    last_timestamp = df['timestamp'].iloc[-1]
    end_date = datetime.now(pytz.timezone('Europe/Athens'))
   
    df2 = get_cy_hist_energy_mix_data(last_timestamp.year, last_timestamp.month, last_timestamp.day, 
                                      end_date.year, end_date.month, end_date.day)
    
    df_final = pd.concat([df,df2])
    
    df_final = df_final.drop_duplicates(subset='timestamp')
    df_final = df_final.set_index('timestamp')
    
    df_final.to_csv('EnergyMix_CY_historical_estimated.csv')
    
    return df_final


def get_cy_weather_historical(lati, longi, start_date, end_date, suffix):

    weather_history = WeatherService().get_weather_history(lati,longi,start_date,end_date,"Europe/Athens")
    weather_history = weather_history.drop('index',axis=1)

    for col in weather_history.columns[1:]:
        weather_history.rename(columns={col: col + suffix}, inplace=True)

    return weather_history


def update_df_cyprus():
    
    df_mix = pd.read_csv('EnergyMix_CY_historical_estimated.csv', index_col='timestamp', parse_dates=True)
    
    df_cyprus = pd.read_csv('df_cyprus.csv', index_col='timestamp', parse_dates=True)

    last_timestamp_mix = df_mix.index[-1]
    last_timestamp_df_cyprus = df_cyprus.index[-1]

    start_date = str(last_timestamp_df_cyprus - timedelta(days=1))[0:10]
    end_date = str(last_timestamp_mix + timedelta(days=1))[0:10]

    # Wind farms
    # ------------
    # Alexigiros windfarm -> https://www.thewindpower.net/windfarm_en_15412_alexigros.php
    df_wind1 = get_cy_weather_historical(34.8694, 33.5168, start_date, end_date, '_wind1')
    # Ayia Anna -> https://www.thewindpower.net/windfarm_en_15926_ayia-anna.php
    df_wind2 = get_cy_weather_historical(34.9609, 33.4916, start_date, end_date, '_wind2')
    # Orites windfarm -> https://www.thewindpower.net/windfarm_en_17098_orites.php
    df_wind3 = get_cy_weather_historical(34.7394, 32.6574, start_date, end_date, "_wind3")
    
#     time.sleep(60)
    
    # PVs
    # -----------
    df_pv1 = get_cy_weather_historical(35.1542, 33.3964, start_date, end_date, "_pv1") # ucy
    df_pv2 = get_cy_weather_historical(34.7404, 32.5336, start_date, end_date, "_pv2") # anarita
    df_pv3 = get_cy_weather_historical(34.6025, 32.9776, start_date, end_date, "_pv3") # akrotiri

#     time.sleep(60)
    
    # Weather big cities
    df_t1 = get_cy_weather_historical(35.1856, 33.3823, start_date, end_date, "_t1") # lefkosia
    df_t2 = get_cy_weather_historical(34.6786, 33.0413, start_date, end_date, "_t2") # lemesos
    df_t3 = get_cy_weather_historical(34.7754, 32.4218, start_date, end_date, "_t3") # pafos

    df_weather_historical = df_wind1.merge(df_wind2, on='date', how='inner').\
                                      merge(df_wind3, on='date', how='inner').\
                                      merge(df_pv1, on='date', how='inner').\
                                      merge(df_pv2, on='date', how='inner').\
                                      merge(df_pv3, on='date', how='inner').\
                                      merge(df_t1, on='date', how='inner').\
                                      merge(df_t2, on='date', how='inner').\
                                      merge(df_t3, on='date', how='inner')

    df_to_add = df_mix[df_mix.index>last_timestamp_df_cyprus]
    df_to_add = df_to_add.join(df_weather_historical.set_index('date'))

    df_cyprus = pd.concat([df_cyprus, df_to_add])
    
    df_cyprus.to_csv('df_cyprus.csv')
    
    return df_to_add

    
def df_train_models_cyprus():
    
    def custom_mape(y_true, y_pred):
        mape = (np.abs(y_pred - y_true) / np.abs(y_true)).map(lambda x: 0 if math.isnan(x) else x)
        mape = mape.map(lambda x: 1 if math.isinf(x) else x)
        return np.mean(mape)
    
    def custom_smape(y_true, y_pred):
        return np.mean((np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred))).map(lambda x: 0 if math.isnan(x) else x))
    
    df_model = pd.read_csv('df_cyprus.csv', index_col='timestamp', parse_dates=True)
    df_model = df_model.reset_index()
    df_model['timestamp'] = pd.to_datetime(df_model['timestamp'], utc = True).dt.tz_convert('Europe/Athens')
    df_model['dow'] = df_model['timestamp'].dt.dayofweek
    df_model['mmonth'] = df_model['timestamp'].dt.month
    df_model['hhour'] = df_model['timestamp'].dt.hour
    df_model = df_model.set_index('timestamp')
    df_model = df_model.asfreq('H')
    df_model = df_model.sort_index()
    df_model = df_model.fillna(method='ffill')

    end_date = str(df_model.reset_index().loc[int(len(df_model)*0.8),'timestamp'])[0:10]
    
    df_test = df_model[int(len(df_model)*0.8):]
    
    
    # WIND MODEL
    
    params = {'num_leaves': 27, 'max_depth': 10, 'learning_rate': 0.0048973487419339806, 'n_estimators': 1220, 'min_child_samples': 72,
          'min_child_weight': 0.11540727433819965, 'subsample': 0.5333324078845113, 'subsample_freq': 1, 
          'colsample_bytree': 0.33881200644162973, 'reg_alpha': 1.3684971130117753e-05, 'reg_lambda': 0.33989551808358526}

    forecaster_wind = ForecasterAutoreg(
                     regressor = LGBMRegressor(random_state=123, verbose = -1, **params),
                     lags      = 2
                 )
    
    forecaster_wind.fit(
            df_model['wind'],
            exog = df_model[['wind_speed_10m_wind1', 'wind_speed_100m_wind1', 'wind_direction_10m_wind1', 'wind_direction_100m_wind1',
                            'wind_gusts_10m_wind1','wind_speed_10m_wind2', 'wind_speed_100m_wind2', 'wind_direction_10m_wind2',
                            'wind_direction_100m_wind2', 'wind_gusts_10m_wind2','wind_speed_10m_wind3', 'wind_speed_100m_wind3',
                            'wind_direction_10m_wind3', 'wind_direction_100m_wind3', 'wind_gusts_10m_wind3']])
    
    save_forecaster(forecaster_wind, file_name='../energy_mix_models/CYPRUS/forecaster_wind.joblib', verbose=False)
    # save_forecaster(forecaster_wind, file_name='forecaster_wind.joblib', verbose=False)


    # TOTAL MODEL

    params = { 'num_leaves': 195, 'max_depth': 13, 'learning_rate': 0.003106611226935988, 'n_estimators': 1455, 'min_child_samples': 14,
          'min_child_weight': 0.002095688192443896, 'subsample': 0.35552760521318666, 'subsample_freq': 4, 'colsample_bytree': 0.43109746009864847,
           'reg_alpha': 0.022433565656815216, 'reg_lambda': 5.329870468192477e-07}    
    
    forecaster_total = ForecasterAutoreg(
                 regressor = LGBMRegressor(random_state=123, verbose = -1, **params),
                 lags      = 24
             )

    forecaster_total.fit(
            df_model['total'],
            exog = df_model[['is_day_t1', 'apparent_temperature_t1', 'apparent_temperature_t2', 'apparent_temperature_t3', 'dow', 'mmonth', 'hhour']])
    
    save_forecaster(forecaster_total, file_name='../energy_mix_models/CYPRUS/forecaster_total.joblib', verbose=False)
    # save_forecaster(forecaster_total, file_name='forecaster_total.joblib', verbose=False)


    # PV MODEL

    params = {'num_leaves': 244, 'max_depth': -1, 'learning_rate': 0.014764863950357537, 'n_estimators': 434, 'min_child_samples': 98,
          'min_child_weight': 0.005899605531472902, 'subsample': 0.5426823518697804, 'subsample_freq': 6, 'colsample_bytree': 0.9427544519130057,
          'reg_alpha': 0.6377700363440638, 'reg_lambda': 0.0001753013841092238}

    forecaster_pv = ForecasterAutoreg(
                 regressor = LGBMRegressor(random_state=123, verbose = -1, **params),
                 lags      = 24
             )
    
    forecaster_pv.fit(
            df_model['pv'],
            exog = df_model[['shortwave_radiation_t2', 'direct_radiation_t2', 'diffuse_radiation_t2', 'direct_normal_irradiance_t2',
                                                      'terrestrial_radiation_t2', 'shortwave_radiation_instant_t2', 'direct_radiation_instant_t2',
                                                      'diffuse_radiation_instant_t2', 'direct_normal_irradiance_instant_t2', 'terrestrial_radiation_instant_t2',
                                                      'shortwave_radiation_t1', 'direct_radiation_t1', 'diffuse_radiation_t1', 'direct_normal_irradiance_t1',
                                                      'terrestrial_radiation_t1', 'shortwave_radiation_instant_t1', 'direct_radiation_instant_t1',
                                                      'diffuse_radiation_instant_t1', 'direct_normal_irradiance_instant_t1', 'terrestrial_radiation_instant_t1',
                                                      'shortwave_radiation_t3', 'direct_radiation_t3', 'diffuse_radiation_t3', 'direct_normal_irradiance_t3',
                                                      'terrestrial_radiation_t3', 'shortwave_radiation_instant_t3', 'direct_radiation_instant_t3']])
                                                      
    save_forecaster(forecaster_pv, file_name='../energy_mix_models/CYPRUS/forecaster_pv.joblib', verbose=False)     
    # save_forecaster(forecaster_pv, file_name='forecaster_pv.joblib', verbose=False)     


    # OIL MODEL
    
    params = {'num_leaves': 123, 'max_depth': 9, 'learning_rate': 0.008500861770816721, 'n_estimators': 1410, 'min_child_samples': 8,
        'min_child_weight': 19.865219659137384, 'subsample': 0.8847123652115201, 'subsample_freq': 10, 'colsample_bytree': 0.21965718397841222,
        'reg_alpha': 0.00014306377991574922, 'reg_lambda': 1.0960999428478195e-08}

    forecaster_oil = ForecasterAutoreg(
                 regressor = LGBMRegressor(random_state=123, verbose = -1, **params),
                 lags      = 24
             )

    forecaster_oil.fit(
        df_model['oil'],
        exog = df_model[['is_day_t1', 'apparent_temperature_t1', 'apparent_temperature_t2', 'apparent_temperature_t3', 'dow', 'mmonth', 'hhour']])
                                            
    save_forecaster(forecaster_oil, file_name='../energy_mix_models/CYPRUS/forecaster_oil.joblib', verbose=False)     
    # save_forecaster(forecaster_oil, file_name='forecaster_oil.joblib', verbose=False)     

    
    
from entsoe import EntsoePandasClient

def get_energy_mix_data_entsoe(start_string, end_string, country_code='PL', timezone='Europe/Warsaw'):

    api_key = '56ec3e0b-6e1d-4537-896e-d6b61556b40e'

    client = EntsoePandasClient(api_key=api_key)

    start = pd.Timestamp(start_string, tz=timezone)
    end = pd.Timestamp(end_string, tz=timezone)

    generation = client.query_generation(country_code, start=start, end=end, psr_type=None)
    
    generation = generation.reset_index()
    generation = generation.rename({'index':'timestamp'},axis=1)
    generation = generation.set_index('timestamp')
    generation['total'] = generation.sum(axis=1)
    generation['wind'] = generation['Wind Onshore']
    generation['oil'] = generation['Fossil Oil']
    generation['gas'] = generation[['Fossil Coal-derived gas', 'Fossil Gas']].sum(axis=1)
    generation['coal'] = generation[['Fossil Brown coal/Lignite', 'Fossil Hard coal']].sum(axis=1)
    generation['biomass'] = generation['Biomass']
    generation['pv'] = generation['Solar']
    generation['water'] = generation[['Hydro Pumped Storage','Hydro Run-of-river and poundage', 'Hydro Water Reservoir']].sum(axis=1)
    generation = generation[['total','wind','oil','gas','coal','biomass','pv','water']]
    generation.columns = ['total','wind','oil','gas','coal','biomass','pv','water']

    return generation
    
    
def update_mix_poland():

    df = pd.read_csv('EnergyMix_PL_historical_estimated.csv', index_col='timestamp', parse_dates=True)
    df = df.reset_index()
    
    last_timestamp = df['timestamp'].iloc[-1]
    end_date = datetime.now(pytz.timezone('Europe/Warsaw'))
   
    df2 = get_energy_mix_data_entsoe(str(last_timestamp)[:10], str(end_date)[:10])
    
    df_final = pd.concat([df.set_index('timestamp'),df2.dropna()])
    df_final = df_final.reset_index()
    
    df_final['timestamp'] = pd.to_datetime(df_final['timestamp'], utc = True).dt.tz_convert('Europe/Warsaw')

    df_final = df_final.drop_duplicates(subset='timestamp')
    df_final = df_final.set_index('timestamp')
    df_final = df_final[df_final.index.minute == 0]
    
    df_final.to_csv('EnergyMix_PL_historical_estimated.csv')
    
    return df_final


def get_pl_weather_historical(lati, longi, start_date, end_date, suffix):

    weather_history = WeatherService().get_weather_history(lati,longi,start_date,end_date,"Europe/Warsaw")
    weather_history = weather_history.drop('index',axis=1)

    for col in weather_history.columns[1:]:
        weather_history.rename(columns={col: col + suffix}, inplace=True)

    return weather_history


def update_df_poland():

    df_mix = pd.read_csv('EnergyMix_PL_historical_estimated.csv', index_col='timestamp', parse_dates=True)

    df_poland = pd.read_csv('df_poland.csv', index_col='timestamp', parse_dates=True)

    last_timestamp_mix = df_mix.index[-1]
    last_timestamp_df_poland = df_poland.index[-1]

    start_date = str(last_timestamp_df_poland - timedelta(days=1))[0:10]
    end_date = str(last_timestamp_mix + timedelta(days=1))[0:10]

    # Wind farms
    # ------------
    # https://www.thewindpower.net/country_zones_en_27_poland.php
    df_wind1 = get_pl_weather_historical(53.4658, 15.1823, start_date, end_date, '_wind1') #Zachodniopomorskie
    df_wind2 = get_pl_weather_historical(54.2944, 18.1531, start_date, end_date, '_wind2') # Pomorskie
    df_wind3 = get_pl_weather_historical(52.28, 17.3523, start_date, end_date, "_wind3") # Wielkopolskie

#     time.sleep(60)

    # PVs
    # ----
    # https://www.power-technology.com/data-insights/top-five-solar-pv-plants-in-operation-in-poland/
    df_pv1 = get_pl_weather_historical(52.0135, 18.63, start_date, end_date, "_pv1") # Turek Solar PV Park https://www.gem.wiki/Przykona_solar_farm
    df_pv2 = get_pl_weather_historical(52.0816, 18.6499, start_date, end_date, "_pv2") # Brudzew Solar PV Park https://www.gem.wiki/Brudzew_solar_farm
    df_pv3 = get_pl_weather_historical(52.6579, 14.882, start_date, end_date, "_pv3") # Witnica Solar PV Park https://www.gem.wiki/Witnica_solar_farm

#     time.sleep(60)

    # Weather big cities
    # ------------------
    # https://www.statista.com/statistics/1455315/poland-largest-cities-by-population/
    df_t1 = get_pl_weather_historical(52.2297, 21.0122, start_date, end_date, "_t1") # warsaw
    df_t2 = get_pl_weather_historical(50.0647, 19.9450, start_date, end_date, "_t2") # krakow
    df_t3 = get_pl_weather_historical(54.3520, 18.6466, start_date, end_date, "_t3") # gdansk

    df_weather_historical = df_wind1.merge(df_wind2, on='date', how='inner').\
                                  merge(df_wind3, on='date', how='inner').\
                                  merge(df_pv1, on='date', how='inner').\
                                  merge(df_pv2, on='date', how='inner').\
                                  merge(df_pv3, on='date', how='inner').\
                                  merge(df_t1, on='date', how='inner').\
                                  merge(df_t2, on='date', how='inner').\
                                  merge(df_t3, on='date', how='inner')

    df_to_add = df_mix[df_mix.index>last_timestamp_df_poland]
    df_to_add = df_to_add.join(df_weather_historical.set_index('date'))

    df_poland = pd.concat([df_poland, df_to_add])

    df_poland.to_csv('df_poland.csv')

    return df_to_add


def df_train_models_poland():
    
    def custom_mape(y_true, y_pred):
        mape = (np.abs(y_pred - y_true) / np.abs(y_true)).map(lambda x: 0 if math.isnan(x) else x)
        mape = mape.map(lambda x: 1 if math.isinf(x) else x)
        return np.mean(mape)
    
    def custom_smape(y_true, y_pred):
        return np.mean((np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred))).map(lambda x: 0 if math.isnan(x) else x))
    
    df_model = pd.read_csv('df_poland.csv', index_col='timestamp', parse_dates=True)
    df_model = df_model.reset_index()
    df_model['timestamp'] = pd.to_datetime(df_model['timestamp'], utc = True).dt.tz_convert('Europe/Warsaw')
    df_model['dow'] = df_model['timestamp'].dt.dayofweek
    df_model['mmonth'] = df_model['timestamp'].dt.month
    df_model['hhour'] = df_model['timestamp'].dt.hour
    df_model = df_model.set_index('timestamp')
    df_model = df_model.asfreq('H')
    df_model = df_model.sort_index()
    df_model = df_model.fillna(method='ffill')

    # WIND MODEL

    params = {'num_leaves': 119, 'max_depth': 3, 'learning_rate': 0.03479461048637985, 'n_estimators': 1023, 
          'min_child_samples': 71, 'min_child_weight': 0.20679050566833018, 'subsample': 0.4619889367961114, 
          'subsample_freq': 2, 'colsample_bytree': 0.1855173640291741, 'reg_alpha': 0.032738220582996046, 
          'reg_lambda': 0.03829325897710832}

    forecaster_wind = ForecasterAutoreg(
                 regressor = LGBMRegressor(random_state=123, verbose = -1, **params),
                 lags      = 1
             )

    forecaster_wind.fit(df_model['wind'],
                        exog = df_model[['wind_speed_10m_wind1', 'wind_speed_100m_wind1', 'wind_direction_10m_wind1', 
                                         'wind_direction_100m_wind1', 'wind_gusts_10m_wind1', 'wind_speed_10m_wind2',
                                         'wind_speed_100m_wind2', 'wind_direction_10m_wind2', 'wind_direction_100m_wind2',
                                         'wind_gusts_10m_wind2', 'wind_speed_10m_wind3', 'wind_speed_100m_wind3', 
                                         'wind_direction_10m_wind3', 'wind_direction_100m_wind3', 'wind_gusts_10m_wind3']])

    save_forecaster(forecaster_wind, file_name='../energy_mix_models/POLAND/forecaster_wind.joblib', verbose=False)


    # TOTAL MODEL

    params = {'num_leaves': 244, 'max_depth': 9, 'learning_rate': 0.0063894380868188575, 'n_estimators': 1191, 
          'min_child_samples': 11, 'min_child_weight': 0.015818036212544302, 'subsample': 0.24106129846799848, 
          'subsample_freq': 5, 'colsample_bytree': 0.2965326867125416, 'reg_alpha': 0.02688967498742564, 
          'reg_lambda': 0.004342800996409992}

    forecaster_total = ForecasterAutoreg(
                 regressor = LGBMRegressor(random_state=123, verbose = -1, **params),
                 lags      = 24
             )

    forecaster_total.fit(
        df_model['total'],
        exog = df_model[['is_day_t1', 'apparent_temperature_t1', 'apparent_temperature_t2', 
                         'apparent_temperature_t3', 'dow', 'mmonth', 'hhour']])

    save_forecaster(forecaster_total, file_name='../energy_mix_models/POLAND/forecaster_total.joblib', verbose=False)


    # PV MODEL

    params = {'n_estimators': 171, 'min_samples_leaf': 1, 'max_depth': 15, 'min_samples_split': 2, 
              'max_features': 'sqrt', 'max_samples': 1.0}

    forecaster_pv = ForecasterAutoreg(
                 regressor = RandomForestRegressor(random_state=123, **params),
                 lags      = 24
             )

    forecaster_pv.fit(
        df_model['pv'],
        exog = df_model[['shortwave_radiation_t2', 'direct_radiation_t2', 'diffuse_radiation_t2', 'direct_normal_irradiance_t2',
                         'terrestrial_radiation_t2', 'shortwave_radiation_instant_t2', 'direct_radiation_instant_t2',
                         'diffuse_radiation_instant_t2', 'direct_normal_irradiance_instant_t2', 'terrestrial_radiation_instant_t2',
                         'shortwave_radiation_t1', 'direct_radiation_t1', 'diffuse_radiation_t1', 'direct_normal_irradiance_t1',
                         'terrestrial_radiation_t1', 'shortwave_radiation_instant_t1', 'direct_radiation_instant_t1',
                         'diffuse_radiation_instant_t1', 'direct_normal_irradiance_instant_t1', 'terrestrial_radiation_instant_t1',
                         'shortwave_radiation_t3', 'direct_radiation_t3', 'diffuse_radiation_t3', 'direct_normal_irradiance_t3',
                         'terrestrial_radiation_t3', 'shortwave_radiation_instant_t3', 'direct_radiation_instant_t3']])

    save_forecaster(forecaster_pv, file_name='../energy_mix_models/POLAND/forecaster_pv.joblib', verbose=False)


    # REMAINDER MODEL
    
    df_model['remainder'] = df_model['total'] - df_model['pv'] - df_model['wind']

    params = {'num_leaves': 239, 'max_depth': 10, 'learning_rate': 0.007403720527114503, 'n_estimators': 1102, 
          'min_child_samples': 82, 'min_child_weight': 0.0016003631971731038, 'subsample': 0.45765815638854773, 
          'subsample_freq': 6, 'colsample_bytree': 0.34827698423195985, 'reg_alpha': 6.97632623787967e-06, 
          'reg_lambda': 9.93303598880603e-08}

    forecaster_remainder = ForecasterAutoreg(
                 regressor = LGBMRegressor(random_state=123, verbose = -1, **params),
                 lags      = 24
             )

    forecaster_remainder.fit(
        df_model['remainder'],
        exog = df_model[['is_day_t1', 'apparent_temperature_t1', 'apparent_temperature_t2', 'apparent_temperature_t3', 
                         'dow', 'mmonth', 'hhour']])

    save_forecaster(forecaster_remainder, file_name='../energy_mix_models/POLAND/forecaster_remainder.joblib', verbose=False)

    
update_mix_cyprus()
update_df_cyprus()
df_train_models_cyprus()

update_mix_poland()
update_df_poland()
df_train_models_poland()