import pandas as pd
from skforecast.utils import load_forecaster
from services import poland_energy_mix_service, cyprus_energy_mix_service

from services.weather import WeatherService

from pandas.tseries.frequencies import to_offset

class CountryEnergyMix(object):

    country: str
    models_path: str

    COUNTRY_CHOICES = [
        ('CYPRUS', 'CYPRUS'),
        ('POLAND', 'POLAND'),]

    RES_LOCATIONS = {
        'CYPRUS': {
            'wind': [(34.8694, 33.5168), (34.9609, 33.4916), (34.7394, 32.6574)],
            'pv': [(35.1542, 33.3964), (34.7404, 32.5336), (34.6025, 32.9776)],
            't': [(35.1856, 33.3823), (34.6786, 33.0413), (34.7754, 32.4218)],
        },
        'POLAND': {
            'wind': [(53.4658, 15.1823), (54.2944, 18.1531), (52.28, 17.3523)],
            'pv': [(52.0135, 18.63), (52.0816, 18.6499), (52.6579, 14.882)],
            't': [(52.2297, 21.0122), (50.0647, 19.9450), (54.3520, 18.6466)],
        }
    }

    COUNTRY_ENERGY_MIX_HISTORY = {
        'CYPRUS': cyprus_energy_mix_service,
        'POLAND': poland_energy_mix_service
    }

    def __init__(self, country: str = "CYPRUS", models_path: str = "energy_mix_models") -> None:
        self.country = country.upper()
        self.models_path = models_path

    def get_model_path_for(self, model_type: str):
        return f"{self.models_path}/{self.country}/forecaster_{model_type}.joblib"

    def get_weather_data(self, forecast_days=2) -> pd.DataFrame:
        ws = WeatherService()
        df_all = None
        for source_type in self.RES_LOCATIONS[self.country]:
            count = 1
            for lat, lon in self.RES_LOCATIONS[self.country][source_type]:
                temp_df = ws.get_weather_forecast(lat, lon, forecast_days=forecast_days)
                suffix = f"_{source_type}{count}"
                temp_df["date"] = pd.to_datetime(temp_df["date"])

                temp_df = temp_df.set_index("date")
                for col in temp_df.columns:
                    if col != "date" and col != "index":
                        temp_df.rename(columns={col: col + suffix}, inplace=True)

                count += 1
                if df_all is None:
                    df_all = temp_df
                else:
                    df_all = df_all.merge(temp_df, how='inner')

                df_all['temp_date'] = temp_df.index
                df_all = df_all.set_index("temp_date")

        return df_all

    def load_models(self):
        pv_path = self.get_model_path_for("pv")
        wind_path = self.get_model_path_for("wind")
        total_path = self.get_model_path_for("total")

        forecaster_pv_loaded = load_forecaster(pv_path, verbose=False)
        forecaster_wind_loaded = load_forecaster(wind_path, verbose=False)
        forecaster_total_loaded = load_forecaster(total_path, verbose=False)

        return forecaster_pv_loaded, forecaster_wind_loaded, forecaster_total_loaded

    def predict_mix(self):
        forecaster_pv_loaded, forecaster_wind_loaded, forecaster_total_loaded = self.load_models()
        df = self.get_weather_data(3)

        country_mix_service = self.COUNTRY_ENERGY_MIX_HISTORY.get(self.country)

        energy_mix_df = country_mix_service.get_pastdays_energy_mix_data()

        df['date'] = pd.to_datetime(df.index)
        df['dow'] = df['date'].dt.dayofweek
        df['mmonth'] = df['date'].dt.month
        df['hhour'] = df['date'].dt.hour
        df = df.asfreq('h')

        energy_mix_df = energy_mix_df.set_index("timestamp")
        energy_mix_df = energy_mix_df.asfreq('h')

        exog_params = df[df['date']>energy_mix_df.index[-1]]

        print("TEST: ", energy_mix_df.index[-1], df)

        # Creating an hourly date range
        steps = len(df[df['date']>energy_mix_df.index[-1]][forecaster_pv_loaded.exog_col_names])

       
        # Force lowercase 'h' frequency by reindexing + setting it explicitly
        # def enforce_lower_h(series):
        #     series = series.asfreq('h')  # Ensures the data is actually hourly
        #     series.index.freq = to_offset('h')  # Force freq attribute
        #     return series

        # def reset_index_with_lower_h(series):
        #     # Step 1: Remove timezone
        #     series = series.tz_localize(None)
            
        #     # Step 2: Build new index with lowercase 'h'
        #     new_index = pd.date_range(start=series.index[0], periods=len(series), freq='h')
        #     series.index = new_index
            
        #     # Optional Step 3: Re-apply timezone
        #     # series = series.tz_localize('Europe/Athens')  # only if you need it later
            
        #     return series
        
        # def strip_freq(series):
        #     series = series.copy()
        #     series.index.freq = None  # Remove freq entirely
        #     return series
        
        # def force_datetime_index(series):
        #     series = series.copy()
            
        #     # If not already a DatetimeIndex, create one based on values
        #     if not isinstance(series.index, pd.DatetimeIndex):
        #         start = pd.to_datetime('now').floor('h') - pd.Timedelta(hours=len(series))
        #         series.index = pd.date_range(start=start, periods=len(series), freq='h')
            
        #     # Strip frequency if present (just in case)
        #     series.index.freq = None
            
        #     return series


        # def force_datetime_index(series):
        #     series = series.copy()
        #     if not isinstance(series.index, pd.DatetimeIndex):
        #         print("WARNING: Fixing non-DatetimeIndex to DatetimeIndex")
        #         start = pd.to_datetime('now').floor('h') - pd.Timedelta(hours=len(series))
        #         series.index = pd.date_range(start=start, periods=len(series), freq='h')
        #     series.index.freq = None  # Strip freq to avoid 'H' vs 'h'
        #     return series

        # last_window_wind = force_datetime_index(energy_mix_df["wind"])
        # print("WIND index type:", type(last_window_wind.index))

        # # last_window_pv = reset_index_with_lower_h(energy_mix_df["pv"].copy())
        # last_window_wind = force_datetime_index(energy_mix_df["wind"].copy())
        # # last_window_total = reset_index_with_lower_h(energy_mix_df["total"].copy())
        # # print("Freqstr check:", last_window_wind.index.freqstr)
        # # print(last_window_wind.index[:5])
        # print(type(last_window_wind.index))          # should be <class 'pandas.DatetimeIndex'>
        # print(last_window_wind.index.freq)           # should be None
        # print(last_window_wind.index.freqstr)        # might error if None, that's okay
        # print(last_window_wind.index[:3])            # show sample of datetimes


        pv_forecast = forecaster_pv_loaded.predict(
            steps=steps, exog=exog_params[forecaster_pv_loaded.exog_col_names], last_window=energy_mix_df["pv"])

        pv_forecast = self.calibrate_pv(pv_forecast, exog_params)

        # last_window_wind = energy_mix_df['wind'].copy()
        # last_window_wind.index.freq = pd.tseries.frequencies.to_offset('h')

        # last_window_wind = enforce_lower_h(energy_mix_df["wind"])

        wind_forecast = forecaster_wind_loaded.predict(steps=steps,
                                     exog=exog_params[forecaster_wind_loaded.exog_col_names],
                                     last_window=energy_mix_df["wind"])

        total_forecast = forecaster_total_loaded.predict(steps=steps,
                                     exog=exog_params[forecaster_total_loaded.exog_col_names],
                                     last_window=energy_mix_df["total"])

        return pv_forecast, wind_forecast, total_forecast

























































    def calibrate_pv(self, pred_pv, exog_params):

        def correct_pv_predictions(pred_pv, shortwave_radiation):
            return 0 if shortwave_radiation == 0 or pred_pv < 0 else pred_pv

        predictions_pv_corrected = \
            pd.DataFrame(
                {'predictions_pv': pred_pv, 'shortwave_radiation_t1': exog_params.shortwave_radiation_t1})

        predictions_pv_corrected['predictions_pv'] = \
            predictions_pv_corrected.apply(
                lambda row: correct_pv_predictions(row.predictions_pv, row.shortwave_radiation_t1), axis=1)

        predictions_pv_corrected = predictions_pv_corrected['predictions_pv']

        return predictions_pv_corrected

