from datetime import datetime

import astral
from astral import sun
import pandas as pd
import openmeteo_requests
# import requests_cache
from requests import Session
from retry_requests import retry
import pytz


class WeatherService(object):
    openmeteo: openmeteo_requests.Client
    FIELDS = ['apparent_temperature',
              'cloud_cover',
              'cloud_cover_high',
              'cloud_cover_low',
              'cloud_cover_mid',
              'diffuse_radiation',
              'diffuse_radiation_instant',
              'direct_normal_irradiance',
              'direct_normal_irradiance_instant',
              'direct_radiation',
              'direct_radiation_instant',
              'global_tilted_irradiance',
              'is_day',
              'precipitation',
              'pressure_msl',
              'rain',
              'relative_humidity_2m',
              'shortwave_radiation',
              'shortwave_radiation_instant',
              'sunshine_duration',
              'surface_pressure',
              'temperature_2m',
              'terrestrial_radiation',
              'terrestrial_radiation_instant',
              'wind_direction_100m',
              'wind_direction_10m',
              'wind_gusts_10m',
              'wind_speed_100m',
              'wind_speed_10m']

    def __init__(self):
        # Setup the Open-Meteo API client with cache and retry on error
        session = Session() #requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

    def get_weather_forecast(self, lat, long, past_days=1, forecast_days=1, timezone='Europe/Athens') -> pd.DataFrame:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": long,
            "hourly": WeatherService.FIELDS,
            "timezone": timezone,
            "past_days": past_days,
            "forecast_days": forecast_days
        }
        return self.make_request(url, params, lat, long, timezone)

    def get_weather_history(self, lat, long, start_date, end_date, timezone='Europe/Athens') -> pd.DataFrame:
        #url = "https://api.open-meteo.com/v1/forecast"
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": long,
            "hourly": WeatherService.FIELDS,
            "timezone": timezone,
            "start_date": start_date,
            "end_date": end_date,
        }

        return self.make_request(url, params, lat, long, timezone)

    def make_request(self, url, params, lat, long, timezone='Europe/Athens') -> pd.DataFrame:
        responses = self.openmeteo.weather_api(url, params=params)

        hourly_dataframe = self.get_hourly_dataframe(responses[0], timezone)
        hourly_dataframe = self.add_sun_data(hourly_dataframe, lat, long, timezone)
        hourly_dataframe = self.add_hours_and_month(hourly_dataframe)

        return hourly_dataframe

    def get_hourly_dataframe(self, response, timezone):
        hourly = response.Hourly()
        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}

        hourly = response.Hourly()
        for i, field_name in enumerate(self.FIELDS):
            hourly_data[field_name] = hourly.Variables(i).ValuesAsNumpy()

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        hourly_dataframe['date'] = hourly_dataframe['date'].dt.tz_convert(timezone)

        # Timezone update and filtering
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)

        return hourly_dataframe[now.hour:].reset_index()

    def add_sun_data(self, hourly_dataframe: pd.DataFrame, latitude: float, longitude: float, timezone='Europe/Athens'):
        loc = astral.LocationInfo(name='Nicosia',
                                  region='Cyprus',
                                  timezone=timezone,
                                  latitude=latitude,
                                  longitude=longitude)
        hourly_dataframe['azimuth'] = hourly_dataframe['date'].map(lambda x: sun.azimuth(loc.observer, x))
        hourly_dataframe['zenith'] = hourly_dataframe['date'].map(lambda x: sun.zenith(loc.observer, x))
        hourly_dataframe['dusk'] = hourly_dataframe['date'].map(lambda x: sun.dusk(loc.observer, x).hour)
        hourly_dataframe['dawn'] = hourly_dataframe['date'].map(lambda x: sun.dawn(loc.observer, x).hour)
        hourly_dataframe['elevation'] = hourly_dataframe['date'].map(lambda x: sun.elevation(loc.observer, x))
        hourly_dataframe['golden_hour_start'] = hourly_dataframe['date'].map(
            lambda x: sun.golden_hour(loc.observer, x)[0].hour)
        hourly_dataframe['golden_hour_end'] = hourly_dataframe['date'].map(
            lambda x: sun.golden_hour(loc.observer, x)[1].hour)
        return hourly_dataframe

    def add_hours_and_month(self, hourly_dataframe: pd.DataFrame):
        hourly_dataframe['month'] = hourly_dataframe['date'].dt.month
        hourly_dataframe['hour'] = hourly_dataframe['date'].dt.hour
        return hourly_dataframe

# print(WeatherService().get_weather_forecast(35.149803, 33.394086))
# angles = pd.read_csv('csv_35.149803_33.394086_fixed_23_180_PT5M.csv')
# angles['datetime'] = angles['period_end'].map(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S+02:00"))
# print(angles[['datetime', 'azimuth', 'zenith']].set_index('datetime'))
