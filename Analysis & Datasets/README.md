# Data & Analysis of the GreenAnalyzer Project

This directory contains all datasets and analysis scripts utilized during the implementation of the GreenAnalyzer project. Each subfolder corresponds to a specific dataset and its associated analysis. Below is an overview of the contents:

### 1. `aerOS-deployment`
- Contains the analysis of the extracted Federated Learning (FL) benchmarking data from the aerOS Pilot 2 deployment.
- Includes additional data generated during the execution of the GreenAnalyzer project that was used in our analysis.

### 2. `energy_mix_prediction`
- Features datasets extracted from energy mix data in Poland and Cyprus, spanning two years. This data was collected via web scraping.
- Contains analyses and models developed for forecasting energy mix trends.

### 3. `energy_profile_modeling`
- Includes data extracted from the pilot nodes and our infrastructure after executing stressor experiments.
- These datasets enable the creation of energy consumption regression models (profiles), which were used in our analysis.

### 4. `pv_panels_energy_production`
- Contains measurements from photovoltaic (PV) panels located in Cyprus. These measurements were used to build energy production prediction models.
- Includes weather data from the same period, providing additional context for the datasets.
- Analysis conducted during the project is documented in Jupyter notebook files. The best models developed are integrated into the GreenAnalyzer framework.

---

### Additional Resource:
The dataset used in the paper *"Energy Modeling of Inference Workloads with AI Accelerators at the Edge: A Benchmarking Study"* (part of GreenAnalyzer) can be found in the following repository:  
[UCY-LINC-LAB/Dataset-and-Analysis-of-Inference-Workloads-with-AI-Accelerators-at-the-Edge](https://github.com/UCY-LINC-LAB/Dataset-and-Analysis-of-Inference-Workloads-with-AI-Accelerators-at-the-Edge)
