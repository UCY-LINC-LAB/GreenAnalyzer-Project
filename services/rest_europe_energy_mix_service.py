import pandas as pd
from entsoe import Area, EntsoePandasClient
from datetime import datetime, timedelta


class RestEuropeEnergyMixService(object):

    api_key: str
    country: str
    country_code: str
    client: EntsoePandasClient

    def __init__(self, api_key: str, country: str):
        self.country_code = self.check_country(country)
        self.api_key = api_key
        self.country = country
        self.client = EntsoePandasClient(api_key=api_key)


    def check_country(self, country):
        country_dict = self.get_countries_dict()
        if country not in country_dict:
            raise Exception("Invalid country")
        return country_dict[country]

    @staticmethod
    def get_countries_dict():
        res = {}
        for area in Area:
            if len(area.name) == 2:
                key = area.meaning.upper().split(",")[0]
                if "/" in key:
                    key = key.split("/")[0].split(" ")[0]
                key = key.replace(" ", "_")
                res[key] = area.name
        return res

    def predict_mix(self):

        # Get the current date and time in the desired timezone
        now = pd.Timestamp(datetime.now(), tz='Europe/Athens')
        # Set the end date to 24 hours from the current time
        tomorrow = now + timedelta(days=3)

        country_code = 'GR'
        wind_and_solar = self.client.query_wind_and_solar_forecast(country_code, start=now, end=tomorrow, psr_type=None)
        wind_and_solar = wind_and_solar.resample('h').first()
        if "Wind Offshore" in wind_and_solar.columns and "Wind Onshore" in wind_and_solar.columns:
            wind_and_solar["wind"] = wind_and_solar["Wind Offshore"] + wind_and_solar["Wind Onshore"]
        elif "Wind Onshore" in wind_and_solar.columns:
            wind_and_solar["wind"] = wind_and_solar["Wind Onshore"]
        overall = self.client.query_load_forecast(country_code, start=now, end=tomorrow)
        overall = overall.resample('h').first()
        overall.columns = ["total"]
        overall["pv"] = wind_and_solar["Solar"]
        overall["wind"] = wind_and_solar["wind"]
        overall = overall.dropna()
        pv_forecast, wind_forecast, total_forecast = overall["pv"], overall["wind"], overall["total"]
        return pv_forecast, wind_forecast, total_forecast