## PV Panels Energy Production

The `pv_panels_energy_production` folder contains datasets, scripts, and analysis notebooks related to the energy production of photovoltaic (PV) panels. It focuses on energy prediction, regression modeling, and data collection from multiple sources. Below is an overview of its structure and contents:

### Subfolders

- **`csvs`**:  
  Likely contains raw or processed CSV datasets relevant to PV panel energy production.

### Files and Notebooks
- **`api_request.ipynb`**:  
  Notebook for making API requests (open-meteo) to collect weather data.

- **`api_request_and_energy_calculation_and_regression_models.ipynb`**:  
  Combines API requests, energy calculations, and regression model development in a single analysis pipeline.

- **`calculations_3_panels - april - openmeteo_everyhour.ipynb`**:  
  Analysis of energy production for three panels using hourly weather data from OpenMeteo for the month of April.

- **`calculations_3_panels - new - openmeteo_everyhour.ipynb`**:  
  An updated notebook for energy calculations of three panels using hourly OpenMeteo data.

- **`calculations_3_panels - november - openmeteo_everyhour.ipynb`**:  
  Analysis of energy production for three panels using hourly OpenMeteo data for the month of November.

- **`calculations_3_panels-tuning.ipynb`**:  
  Focuses on parameter tuning for energy calculations related to three panels.

- **`classification_models_fluctuations.ipynb`**:  
  Develops classification models to analyze and predict fluctuations in energy production.

- **`get_dataset_from_prometheus.ipynb`**:  
  Script for retrieving datasets from Prometheus, likely for monitoring or energy production metrics.

- **`regression_models-openmeteo-hour-and-energy.ipynb`**:  
  Notebook focused on developing regression models for hourly energy production using OpenMeteo data.

---

### Purpose
This folder consolidates data collection, energy prediction modeling, and fluctuation analysis for PV panels. The notebooks cover various aspects, including weather-based energy production forecasts, regression models, and classification techniques, supporting the overall goal of energy production analysis and prediction.
