#!/usr/bin/env python
# coding: utf-8

# PREPROCESSING

import pandas as pd
import datetime

import pytz
import pickle

from services.weather import WeatherService
from services.modeler import NaiveModel, MathModel, AIModel
from services.pv_parameters import find_params

from django.core.files import File
import os

def preprocessing_and_training(serializer): # serializer, data_path

    # name=serializer.validated_data['name']
    # date_col=serializer.validated_data['date_col']
    # pv_col=serializer.validated_data['energy_col']
    # latitude=serializer.validated_data['lat']
    # longitude=serializer.validated_data['lon']
    # timezone=serializer.validated_data['timezone']
    # model_type=serializer.validated_data['model_type']
    # panel_tilt=serializer.validated_data['panel_tilt']
    # panel_size=serializer.validated_data['panel_size']
    # n_trials=serializer.validated_data['n_trials']
    # optimize_metric=serializer.validated_data['optimize_metric']

    name=serializer.name
    date_col=serializer.date_col
    pv_col=serializer.energy_col
    latitude=serializer.lat
    longitude=serializer.lon
    timezone=serializer.timezone
    model_type=serializer.model_type
    panel_tilt=serializer.panel_tilt
    panel_size=serializer.panel_size
    n_trials=serializer.n_trials
    optimize_metric=serializer.optimize_metric
    data_path = serializer.csv_file.name

    df = pd.read_csv(data_path, index_col=date_col, parse_dates=True, infer_datetime_format=True)
    df.reset_index(inplace=True)
    df = df[[date_col,pv_col]]
    df = df.sort_values(date_col)
    df = df.dropna(subset=[pv_col])

    df['diff_days'] = df[date_col].diff().dt.days
    n = sum(df['diff_days']>1)

    # Some preprocessing steps

    def preprocessing(data) :
    
        data = data.drop(['diff_days'], axis=1)

        start = data[date_col].iloc[0].replace(microsecond=0, second=0, minute=0)
        end = data[date_col].iloc[-1].replace(microsecond=0, second=0, minute=0)
        to_add = pd.DataFrame.from_dict({date_col:[start]})
        to_add[pv_col] = None
        data = pd.concat([to_add,data],ignore_index=True)

        list_of_indexes = list(data[date_col])
        s = data.shape[0]

        date_now = start

        while date_now!=end :
            if not date_now in list_of_indexes :
                data.loc[s,date_col] = date_now
            date_now = date_now + datetime.timedelta(hours=1) 
            # check for 1 hour because this is the interval of different data points for the weather data
            s += 1
        
        data = data.sort_values(by=date_col)

        ## rolling window & keep only rows at 1 hour

        data = data.set_index(date_col).sort_index()
        data = data.rolling(window=pd.Timedelta(hours=1),center=True).mean()
        data = data.reset_index()
        data = data[data[date_col].dt.minute == 0]
        data = data[data[date_col].dt.second == 0]

        ## fix timezones

        data_timezone = pytz.timezone(timezone)
        data[date_col] = data.apply(lambda x : pytz.timezone(timezone).localize(x[date_col], is_dst=True),axis=1)

        start_date = str(data[date_col][0] - datetime.timedelta(days=1))[0:10]
        end_date = str(data[date_col].iloc[len(data)-1] + datetime.timedelta(days=1))[0:10]

        data = data[(data[date_col]>start_date) & (data[date_col]<end_date)]
        
        ## api call

        weather_history = WeatherService().get_weather_history(latitude,longitude,start_date,end_date,timezone)
        weather_history = weather_history.drop('index',axis=1)
       
        # weather_forecast = WeatherService().get_weather_forecast(latitude,longitude,timezone=timezone) 
        # #weather_forecast = weather_forecast.drop('index',axis=1)

        ## join

        data = data.set_index(date_col).join(weather_history.set_index(date_col))

        return data
    
    if n==0:
        df = preprocessing(df)

    else :
        periods = list(df[df['diff_days']>1][date_col])
        periods = periods+[df[date_col].iloc[0],df[date_col].iloc[-1]]
        periods = sorted(periods)

        dfdf = df.copy()
        df = pd.DataFrame()

        for i in range(n+1) :
            dfi = dfdf[(dfdf[date_col]>=periods[i]) & (dfdf[date_col]<periods[i+1])]
            dfi = preprocessing(dfi)
            df = pd.concat([df,dfi])

    data = df.copy()


    # MODELS

    ## Naive model

    if model_type == 'NAIVE':
        m = NaiveModel()
        m.dataset = data
        m.target = pv_col
        m.radiation_feature = 'shortwave_radiation'
        m.generate_model()

        serializer.parameters = {'delta':m.delta}

        serializer.save()


    ## Math Model

    if model_type == 'MATH':
        p = find_params(df=data, pv_col=pv_col, panel_tilt=panel_tilt, panel_size=panel_size, n_trials=n_trials)

        d = p.copy()
        p = {'panel_size':panel_size, 'panel_tilt':panel_tilt}
        p.update(d)
        
        serializer.parameters = p

        serializer.save()


    ## AI model

    if model_type == 'AI':

        fields = sorted(['apparent_temperature', 'cloud_cover', 
           'cloud_cover_high', 'cloud_cover_low', 'cloud_cover_mid',
           'diffuse_radiation', 'diffuse_radiation_instant',
           'direct_normal_irradiance', 'direct_normal_irradiance_instant',
           'direct_radiation', 'direct_radiation_instant',
           'global_tilted_irradiance', 'is_day', 'precipitation', 'pressure_msl',
           'rain', 'relative_humidity_2m', 'shortwave_radiation',
           'shortwave_radiation_instant', 'sunshine_duration', 'surface_pressure',
           'temperature_2m', 'terrestrial_radiation',
           'terrestrial_radiation_instant', 'wind_direction_100m',
           'wind_direction_10m', 'wind_gusts_10m', 'wind_speed_100m',
           'wind_speed_10m', 'azimuth', 'zenith', 'dusk', 'dawn', 'elevation',
           'golden_hour_start', 'golden_hour_end', 'month', 'hour'])

        data[pv_col] = data[pv_col].fillna(0)

        m = AIModel()
        m.dataset = data
        m.target = pv_col
        m.params['end'] = data.reset_index().loc[int(len(data.reset_index()[date_col])*0.8),date_col]
        m.params['timestamp_param'] = date_col
        m.params['features'] = fields
        m.params['optimize_metric'] = optimize_metric
        m.generate_model()

        m.model_path = name
        m.store_model()

        model_file_path = m.model_path+'.pkl'
        with open(model_file_path, 'rb') as model_file:
            serializer.stored_model = File(model_file)
            serializer.save()
        os.remove(model_file_path)




