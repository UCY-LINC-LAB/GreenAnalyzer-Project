# Import libraries
import requests
import pandas as pd
from datetime import datetime, timedelta, date
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pytz

# Setup the Open-Meteo API client with cache and retry on error
# cache_session = requests_cache.CachedSession('.cache', expire_after=60*60)
# retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
# openmeteo = openmeteo_requests.Client(session=retry_session)
openmeteo = openmeteo_requests.Client()


def get_cy_temp_historical(lati, longi, suffix, start_date, end_date):

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
          "latitude": lati,
          "longitude": longi,
          "start_date": start_date,
          "end_date": end_date,
          "hourly": "shortwave_radiation",
          "timezone": "Europe/Moscow"
      }

    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_shortwave_radiation = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
          start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
          end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
          freq = pd.Timedelta(seconds = hourly.Interval()),
          inclusive = "left"
      )}

    hourly_data["shortwave_radiation"] = hourly_shortwave_radiation

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_dataframe['date'] = hourly_dataframe['date'].dt.tz_convert('Europe/Athens')

    # Adding suffix to columns 2 to 4
    for col in hourly_dataframe.columns[1:]:  # Columns 2 to end
        hourly_dataframe.rename(columns={col: col + suffix}, inplace=True)

    return hourly_dataframe

def get_cy_hist_energy_mix_data(start_yyyy, start_mm, start_dd, end_yyyy, end_mm, end_dd):

    # Define the start and end dates
    start_date = datetime(int(start_yyyy), int(start_mm), int(start_dd))
    end_date = datetime(int(end_yyyy), int(end_mm), int(end_dd))
    # print(start_date.strftime("%Y-%m-%d"))

    # Calculate the difference in days
    delta = end_date - start_date

    df = pd.DataFrame()

    # Iterate over the range of days
    for i in range(delta.days + 1):

        day = start_date + timedelta(days=i)
        url = "https://tsoc.org.cy/electrical-system/archive-total-daily-system-generation-on-the-transmission-system/?startdt=" + day.strftime("%d-%m-%Y") + "&enddt=%2B1days"

        # Fetch the data
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Assuming the data is in a table format in the HTML
            df = pd.concat([df, pd.read_html(response.text)[1]], ignore_index=True)
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    df.columns = ['timestamp', 'total_conv_avail', 'wind', 'renewable', "total", "conventional"]

    df = df[['timestamp', "total", "wind", "renewable", "conventional"]]

    df['timestamp'] =  pd.to_datetime(df['timestamp']).dt.tz_localize('Europe/Athens', ambiguous = "NaT", nonexistent = "NaT")

    # Merge with hourly solar irradiance values
    df = pd.merge(
          df,
          get_cy_temp_historical(35.19, 33.38, "_nic", start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
          left_on = 'timestamp', right_on = "date", how = "right"
      )

    # Drop rows with missing values (intention: delete rows for the current day for hours still to come)
    df = df.dropna(axis=0, how='any')

    # Assumption all conventional productions comes from oil
    df['oil'] = df['conventional']
    df['gas'] = 0
    df['coal'] = 0

    # Assumption: no sunshine at midnight => all renewable comes from biomass => this value is assumed throughout the day
    biomass_value = df['renewable'].iloc[0]
    df['pv'] = df.apply(lambda row: row.renewable - biomass_value if row.shortwave_radiation_nic > 0 else 0, axis = 1)
    df['biomass'] = df.apply(lambda row: row.renewable if row.shortwave_radiation_nic == 0 else biomass_value, axis=1)

    # df['pv'] = df.apply(lambda row: row.renewable - row.biomass if row.direct_normal_irradiance_nic >0 else 0, axis = 1)
    # df['pv'] = df.apply(lambda row: row.renewable - row.biomass, axis = 1)

    df['water'] = 0

    return df[['timestamp', 'total', 'wind', 'oil', 'gas', 'coal', 'biomass', 'pv', 'water']]


def get_cy_temp_forecast(lati, longi, suffix, past_days=0, forecast_days=1):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lati,
        "longitude": longi,
        "hourly": "shortwave_radiation",
        "timezone": "Europe/Moscow",
        "past_days": past_days,
        "forecast_days": forecast_days
    }

    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_shortwave_radiation = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ), "shortwave_radiation": hourly_shortwave_radiation}

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    hourly_dataframe['date'] = hourly_dataframe['date'].dt.tz_convert('Europe/Athens')

    # Adding suffix to columns 2 to 4
    for col in hourly_dataframe.columns[1:]:  # Columns 2 to end
        hourly_dataframe.rename(columns={col: col + suffix}, inplace=True)

    return hourly_dataframe


def get_cy_current_energy_mix_data(num_past_days=3):
    # Define the start and end dates
    start_date = datetime.now(pytz.timezone('Europe/Athens')).date()  #date.today()
    # print(start_date)

    df = pd.DataFrame()

    url = "https://tsoc.org.cy/electrical-system/archive-total-daily-system-generation-on-the-transmission-system/?startdt=" + \
          start_date.strftime("%d-%m-%Y") + "&enddt=%2B1days"

    # Fetch the data
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Assuming the data is in a table format in the HTML
        df = pd.read_html(response.text)[1]
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

    df.columns = ['timestamp', 'total_conv_avail', 'wind', 'renewable', "total", "conventional"]

    df = df[['timestamp', "total", "wind", "renewable", "conventional"]]

    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize('Europe/Athens', ambiguous="NaT",
                                                                     nonexistent="NaT")

    # Merge with hourly solar irradiance values
    df = pd.merge(
        df,
        get_cy_temp_forecast(35.19, 33.38, "_nic"),
        left_on='timestamp', right_on="date", how="left"
    )

    # Assumption all conventional productions comes from oil
    df['oil'] = df['conventional']
    df['gas'] = 0
    df['coal'] = 0

    # Assumption: no sunshine at midnight => all renewable comes from biomass => this value is assumed throughout the day
    biomass_value = df['renewable'].iloc[0]
    df['pv'] = df.apply(lambda row: row.renewable - biomass_value if row.shortwave_radiation_nic > 0 else 0, axis=1)
    df['biomass'] = df.apply(lambda row: row.renewable if row.shortwave_radiation_nic == 0 else biomass_value, axis=1)

    df['water'] = 0

    df = df.dropna(axis=0, how='any')

    return df[['timestamp', 'total', 'wind', 'oil', 'gas', 'coal', 'biomass', 'pv', 'water']].tail(1)


def get_pastdays_energy_mix_data(num_past_days=3):
    # Define the start and end dates
    end_date = datetime.now(pytz.timezone('Europe/Athens'))
    start_date = end_date - timedelta(days=num_past_days)

    # Calculate the difference in days
    delta = end_date - start_date

    df = pd.DataFrame()

    # Iterate over the range of days
    for i in range(delta.days + 1):

        day = start_date + timedelta(days=i)
        url = "https://tsoc.org.cy/electrical-system/archive-total-daily-system-generation-on-the-transmission-system/?startdt=" + day.strftime(
            "%d-%m-%Y") + "&enddt=%2B1days"

        # Fetch the data
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Assuming the data is in a table format in the HTML
            df = pd.concat([df, pd.read_html(response.text)[1]], ignore_index=True)
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    df.columns = ['timestamp', 'total_conv_avail', 'wind', 'renewable', "total", "conventional"]

    df = df[['timestamp', "total", "wind", "renewable", "conventional"]]

    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize('Europe/Athens', ambiguous="NaT",
                                                                     nonexistent="NaT")

    # Merge with hourly solar irradiance values
    df = pd.merge(
        df,
        get_cy_temp_forecast(35.19, 33.38, "_nic", 3, 2),
        left_on='timestamp', right_on="date", how="right"
    )

    # Drop rows with missing values (intention: delete rows for the current day for hours still to come)
    df = df.dropna(axis=0, how='any')

    # Assumption all conventional productions comes from oil
    df['oil'] = df['conventional']
    df['gas'] = 0
    df['coal'] = 0

    # Assumption: no sunshine at midnight => all renewable comes from biomass => this value is assumed throughout the day
    biomass_value = df['renewable'].iloc[0]
    df['pv'] = df.apply(lambda row: row.renewable - biomass_value if row.shortwave_radiation_nic > 0 else 0, axis=1)
    df['biomass'] = df.apply(lambda row: row.renewable if row.shortwave_radiation_nic == 0 else biomass_value, axis=1)

    df['water'] = 0

    return df[['timestamp', 'total', 'wind', 'oil', 'gas', 'coal', 'biomass', 'pv', 'water']].tail(num_past_days * 24)
