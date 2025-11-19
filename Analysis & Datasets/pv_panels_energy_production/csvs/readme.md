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

