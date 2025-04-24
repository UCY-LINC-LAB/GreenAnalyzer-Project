import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz


def get_pastdays_energy_mix_data(num_past_days=3):

    # Define the API endpoint
    url = "https://api.raporty.pse.pl/api/his-wlk-cal"

    # Get the current time in the Europe/Warsaw timezone
    warsaw_tz = pytz.timezone('Europe/Warsaw')
    now_warsaw = datetime.now(warsaw_tz)

    # Get the current date in the Europe/Warsaw timezone
    current_date_warsaw = now_warsaw.date()

    # Compute the previous date
    previous_date = current_date_warsaw - timedelta(days=num_past_days)

    # Format the previous date as a string in YYYY-MM-DD format
    previous_date_str = previous_date.strftime('%Y-%m-%d')

    # Define the parameters with the previous date
    params = {
        "$filter": f"business_date ge '{previous_date_str}'",
        "$first": 1000
    }

    # Make the GET request to the API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract the list of records
        records = data.get("value", [])

        # Create a DataFrame from the list of records
        df = pd.DataFrame(records)

        # Select the specific columns and drop rows with any missing values
        selected_columns = ["udtczas", "zapotrzebowanie", "pv", "wi"]
        df_selected = df[selected_columns].dropna(how="any")

        # Convert 'udtczas' column to datetime and set timezone to Warsaw
        df_selected['udtczas'] = pd.to_datetime(df_selected['udtczas'], utc=False).dt.tz_localize('Europe/Warsaw')

        # Generate hourly date range for the last 24 hours in Warsaw timezone
        now = datetime.now(pytz.timezone('Europe/Warsaw'))
        date_range = pd.date_range(end=now, periods=24, freq='H', tz='Europe/Warsaw')

        # Create a DataFrame from the date range
        df_date_range = pd.DataFrame(date_range, columns=["udtczas"])
        df_date_range['udtczas'] = df_date_range['udtczas'].dt.floor('H')

        # Perform an inner join on 'udtczas'
        df_PL_hist_final = pd.merge(df_date_range, df_selected, on="udtczas", how="left")

        # Forward fill missing values for specific columns
        columns_to_fill = ["zapotrzebowanie", "pv", "wi"]
        df_PL_hist_final[columns_to_fill] = df_PL_hist_final[columns_to_fill].fillna(method='ffill')
        df_PL_hist_final.columns = ['timestamp', 'total', 'pv', 'wind']

        # ------------------------------------------------------------------------------------------------------------
        # GET THE ENERGY MIX
        # ------------------------------------------------------------------------------------------------------------

        # Assuptions:
        # 1) For simplicity purposes, the carbon footprint of the electricity imported through interconnections will be neglected.
        # 2) For renewable sources of electrcity, there were historical data only for wind and solar farm energy generation.
        #    Hydro power was assumed to be a constant of 1.3% of the total electrcity generation based on the following article:
        #    https://notesfrompoland.com/2024/01/03/poland-produced-record-26-of-electricity-from-renewables-in-2023/
        #    The rest of the electricity generation comes from conventional power sources (oil, gas, coal)
        # 3) The themal power will be attributed to the different sources as follows:
        #    https://notesfrompoland.com/2024/01/03/poland-produced-record-26-of-electricity-from-renewables-in-2023/
        #    However, coal continued to account for almost two thirds of power production in Poland, with hard coal generating
        #    65.27 TWh (43%) and brown coal (lignite) 31.47 TWh (20.8%). Gas accounted for a further 12.94 TWh (8.5%)
        #    and oil 2.54 TWh (1.7%).

        df_PL_hist_final['water'] = round(df_PL_hist_final['total'] * 0.013, 3)

        df_PL_hist_final['thermal'] = df_PL_hist_final['total'] - df_PL_hist_final['wind'] - df_PL_hist_final['pv'] - df_PL_hist_final['water']

        df_PL_hist_final['oil'] = round((2.54) / (65.27 + 31.47 + 12.94 + 2.54) * df_PL_hist_final['thermal'], 3)

        df_PL_hist_final['gas'] = round((12.94) / (65.27 + 31.47 + 12.94 + 2.54) * df_PL_hist_final['thermal'], 3)

        df_PL_hist_final['coal'] = round((65.27 + 31.47) / (65.27 + 31.47 + 12.94 + 2.54) * df_PL_hist_final['thermal'], 3)

        df_PL_hist_final['biomass'] = 0

        df_PL_hist_final['other'] = 0

        # Print the DataFrame with the selected columns
        return df_PL_hist_final[['timestamp', 'total', 'wind', 'oil', 'gas', 'coal', 'biomass', 'pv', 'water']]

    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
        return None