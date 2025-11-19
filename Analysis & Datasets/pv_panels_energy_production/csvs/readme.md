# CSV files

This file provides detailed information about the CSV files in this folder.

## Inverters Files

These files contain measurements of the power produced by the facility’s PV panels. The data were collected from the inverters and retrieved using the Prometheus interface.

Each file includes the following columns:

* date: Timestamp of the measurement (recorded every 15 seconds)

* inverter1: Power produced by PV panel 1 (W)

* inverter2: Power produced by PV panel 2 (W)

* inverter3: Power produced by PV panel 3 (W)

The file names indicate the date range covered by the data they contain:

* inverters_03.11.2023-09.02.2024.csv

* inverters_18.04.2024-04.05.2024.csv

* inverter_07.06.2024-25.06.2024.csv

## Math model Files

These files contain hourly data for the mathematical models. They include weather variables retrieved from the Open-Meteo API ([open-meteo API](https://open-meteo.com/)), solar angle information computed with the Astral library ([astral library](https://astral.readthedocs.io/en/latest/)), intermediate variables used internally by the model, the true power values produced by the PV panels, the corresponding predicted values, and the resulting percentage error.

Columns

* datetime, time: Timestamps of the hourly measurements

* inverterX: True power produced by PV panel X

* temperature_2m (°C), relative_humidity_2m (%), apparent_temperature (°C), precipitation (mm), rain (mm), cloud_cover (%), cloud_cover_low (%), cloud_cover_mid (%), cloud_cover_high (%), wind_speed_10m (km/h), wind_speed_100m (km/h), wind_gusts_10m (km/h), is_day, sunshine_duration (s), shortwave_radiation (W/m²), direct_radiation (W/m²), diffuse_radiation (W/m²), direct_normal_irradiance (W/m²), global_tilted_irradiance (W/m²), terrestrial_radiation (W/m²), shortwave_radiation_instant (W/m²), direct_radiation_instant (W/m²), diffuse_radiation_instant (W/m²), direct_normal_irradiance_instant (W/m²), terrestrial_radiation_instant (W/m²): Weather variables obtained from the Open-Meteo API

* azimuth, zenith: Solar angles calculated using the Astral library

* Gpoa (W/m²): Internal variable required by the mathematical model

* energyX: Predicted energy or power produced for PV panel X

* errorX: Percentage error for PV panel X

*Note:*
For the file *math_model_all_inverters_03.11.2023-25.06.2024.csv*, the suffix X is omitted from the columns names. This file corresponds to a trial where all inverters were treated as a single group to produce one unified model.

Like for the inverters files the file names indicate the date range covered by the data they contain:

* math_model_03.11.2023-09.02.2024.csv
* math_model_07.06.2024-25.06.2024.csv
* math_model_18.04.2024-04.05.2024.csv
* math_model_all_inverters_03.11.2023-25.06.2024.csv

## Weather data Files

These files contain weather data retrieved from the Open-Meteo API ([open-meteo API](https://open-meteo.com/)) for the geolocation latitude = 35.15, longitude = 33.40, obtained either through direct API requests or by downloading CSV files.

### Files obtained through direct API requests

Columns:

* time: Timestamps of the hourly measurements
* temperature_2m (°C), relative_humidity_2m (%), dew_point_2m (°C), apparent_temperature (°C), precipitation (mm), rain (mm), snowfall (cm), snow_depth (m), weather_code (wmo code), pressure_msl (hPa), surface_pressure (hPa), cloud_cover (%), cloud_cover_low (%), cloud_cover_mid (%), cloud_cover_high (%), et0_fao_evapotranspiration (mm), vapour_pressure_deficit (kPa), wind_speed_10m (km/h), wind_speed_100m (km/h), wind_direction_10m (°), wind_direction_100m (°), wind_gusts_10m (km/h), soil_temperature_0_to_7cm (°C), soil_temperature_7_to_28cm (°C), soil_temperature_28_to_100cm (°C), soil_temperature_100_to_255cm (°C), soil_moisture_0_to_7cm (m³/m³), soil_moisture_7_to_28cm (m³/m³), soil_moisture_28_to_100cm (m³/m³), soil_moisture_100_to_255cm (m³/m³), is_day (), sunshine_duration (s), shortwave_radiation (W/m²), direct_radiation (W/m²), diffuse_radiation (W/m²), direct_normal_irradiance (W/m²), global_tilted_irradiance (W/m²), terrestrial_radiation (W/m²), shortwave_radiation_instant (W/m²), direct_radiation_instant (W/m²), diffuse_radiation_instant (W/m²), direct_normal_irradiance_instant (W/m²), global_tilted_irradiance_instant (W/m²), terrestrial_radiation_instant (W/m²): Weather variables

Like previously, the file names indicate the date ranges covered:

* weather_data_01.06.2023-01.06.2024.csv
* weather_data_01.06.2024-26.06.2024.csv

### Files obtained by downloading CSV files

Columns:

* air_temp, albedo, azimuth, clearsky_dhi, clearsky_dni, clearsky_ghi, clearsky_gti, cloud_opacity, dewpoint_temp, dhi, dni, ghi, gti, precipitable_water, precipitation_rate, relative_humidity, surface_pressure, snow_depth, snow_water_equivalent, snow_soiling_rooftop, snow_soiling_ground, wind_direction_100m, wind_direction_10m, wind_speed_100m, wind_speed_10m, zenith: Weather Variables
* period_end: Timestamp of the measurement (recorded every 5 minutes)
* period: Duration since the previous measurement (e.g., PT5M = 5 minutes)

Like previously, the file names indicate the date ranges covered:

* weather_data_01.06.2023-30.06.2023.csv
* weather_data_01.10.2023-05.06.2024.csv
