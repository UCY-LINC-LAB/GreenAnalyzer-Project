import math
from dataclasses import dataclass, field
import pandas as pd
from pycaret.regression import setup, compare_models, tune_model, save_model, load_model, add_metric, get_metrics
import json
import logging
from typing import List, Dict, Optional, Any, Tuple

import xgboost
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)


@dataclass
class Model:
    model_path: str = None
    model_name: str = None
    target: str = "energy"
    params: Dict[str, Any] = field(default_factory=dict)
    model: Optional[Any] = None
    dataset: Optional[pd.DataFrame] = None
    models_path: str = "/models/"

    def compute_predictions(self, X_test: pd.DataFrame, field_name: str = "pred") -> pd.DataFrame:
        raise NotImplementedError("This method should be overridden by subclasses")

    def generate_model(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def store_model(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def retrieve_model(self):
        raise NotImplementedError("This method should be overridden by subclasses")


def validation_results(model, target: str, extra_feature: str, X_test: pd.DataFrame, y_test: pd.Series) -> float:
    X_test["pred"] = model.compute_predictions(X_test)#[model.feature_names_in_])
    X_test[target] = y_test
    predictions = X_test.sort_index()
    predictions.loc[predictions[extra_feature] == 0, 'pred'] = 0
    res = 2 * abs(predictions[target] - predictions['pred']) / (predictions[target] + predictions['pred'])
    res = res.fillna(0)
    res[res == 2] = 0
    return res.mean()
    #return 2 * 100 * np.mean((np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred))).map(lambda x: 0 if math.isnan(x) else x))


# def validation_results_from_predictions(pred: str, target: str, extra_feature: str, predictions: pd.DataFrame) -> float:
#     predictions.loc[predictions[extra_feature] == 0, pred] = 0
#     res = 2 * abs(predictions[target] - predictions[pred]) / (predictions[target] + predictions[pred])
#     res = res.fillna(0)
#     res[res == 2] = 0
#     return res.mean()*100


@dataclass
class AIModel(Model):
    params: Dict[str, Any] = field(default_factory=lambda: {
        "features": list[str],
        "end": None,
        "timestamp_param": 'datetime',
        "included_models": ['rf', 'et', 'gbr', 'br', 'xgboost', 'ada'],
        "optimize_metric": None
    })

    def generate_model(self) -> Tuple[Any, pd.DataFrame, pd.Series]:
        features = self.params["features"]
        end = self.params["end"]
        timestamp_param = self.params["timestamp_param"]
        included_models = self.params["included_models"]
        optimize_metric = self.params["optimize_metric"]
        
        def smape_metric(y_true, y_pred):
            return 2 * 100 * np.mean((np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred))).map(lambda x: 0 if math.isnan(x) else x))
 
        data = self.dataset[[self.target] + features].reset_index()
        data_train, data_test = data, data

        if end is not None:
            data_train = data.loc[data[timestamp_param] < end]
            data_test = data.loc[data[timestamp_param] >= end]

        data_train = data_train.set_index(timestamp_param)
        data_test = data_test.set_index(timestamp_param)

        X_test = data_test[features]
        y_test = data_test[self.target]

        setup(data=data_train, target=self.target, session_id=123, fold=5)
        
        add_metric("smape", "SMAPE", score_func=smape_metric, greater_is_better=False)

        get_metrics(include_custom=True, raise_errors=True)
         
        best_model = compare_models(include=included_models, sort=optimize_metric)
        best_model = tune_model(best_model, n_iter=40, choose_better=True, optimize=optimize_metric)
        self.model = best_model

        logging.info("Model generated successfully")
        return best_model, X_test, y_test

    def store_model(self):
        save_model(self.model, self.model_path)
        logging.info("Model stored successfully")

    def retrieve_model(self) -> Any:
        self.model = load_model(self.model_path)
        logging.info("Model retrieved successfully")
        return self.model

    def compute_predictions(self, X_test: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            raise ValueError("Model is not trained yet")

        # Solve issues with columns identification
        #columns = list(set(X_test.columns).intersection(set(self.model.feature_names_in_)))
        #columns = list(self.model.feature_names_in)

        return self.model.predict(X_test)


@dataclass
class NaiveModel(Model):
    params: Dict[str, Any] = field(default_factory=lambda: {})
    radiation_feature: str = "shortwave_radiation"
    delta: float = None

    def compute_predictions(self, X_test: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            raise ValueError("The model is not trained")
        return X_test.apply(lambda x: self.model.predict(x["shortwave_radiation"]), axis=1)

    def generate_model(self):
        self.delta = self.dataset[self.target].max() / self.dataset[self.radiation_feature].max()
        self.create_model_from_delta()

        logging.info(f"Model generated with delta: {self.delta}")

    def store_model(self):
        pass

    def retrieve_model(self):
        if 'delta' in self.params:
            self.delta = self.params["delta"]
        else:
            raise ValueError("The model has not been trained yet")
        self.create_model_from_delta()
        logging.info("Model parameters retrieved successfully")

    def create_model_from_delta(self):
        delta: float = self.delta

        class TempModel(object):
            predict = lambda _self, x: delta * x

        self.model = TempModel()


@dataclass
class MathModel(Model):

    @staticmethod
    def calculate_energy(DNI, DHI, GHI, thz, gs, air_temp, panel_size, panel_tilt, performance_ratio, system_losses, g,
                         nameplate, inverter_transformer, mismatch, connections, dc_wiring, ac_wiring, soiling,
                         availability, shading, sun_tracking, age, *args, **kwargs):

        derating_factor = nameplate * inverter_transformer * mismatch * connections * dc_wiring * ac_wiring * soiling * availability * shading * sun_tracking * age

        b = panel_tilt
        albedo = 0.2  # ground reflectance (default value)

        # Convert degrees to radians
        thz_rad = math.radians(thz)
        b_rad = math.radians(b)
        gs_rad = math.radians(gs)
        g_rad = math.radians(g)

        # Calculate the angle of incidence th
        cos_th = (math.sin(thz_rad) * math.cos(gs_rad - g_rad) * math.sin(b_rad) + math.cos(thz_rad) * math.cos(b_rad))

        # Ensure cos_th is within the valid range
        cos_th = max(0, min(cos_th, 1))

        # Direct component
        Gpoa_direct = DNI * cos_th

        # Diffuse component (assumed isotropic)
        Gpoa_diffuse = DHI * (1 + math.cos(b_rad)) / 2

        # Reflected component
        Gpoa_reflected = GHI * albedo * (1 - math.cos(b_rad)) / 2

        # Total Gpoa
        Gpoa = Gpoa_direct + Gpoa_diffuse + Gpoa_reflected

        # Global constants
        Eo = 1000  # Reference Irradiance (W/m²)
        To = 25  # Reference Temperature (°C)
        g = -0.0042  # Power Temperature Coefficient (%/°C)
        Pmp0 = 270  # PV module rated power (Wp)

        # NOCT (Nominal Operating Cell Temperature)
        NOCT = 48

        # Insolation in mW/cm²
        S = 80

        # Calculate module temperature
        Tm = air_temp + ((NOCT - 20) / 80) * S

        # Calculate predicted power production
        if Gpoa >= 125:
            p = ((Gpoa / Eo) * Pmp0 * (1 + g * (Tm - To))) * derating_factor
        else:
            p = ((0.008 * (Gpoa ** 2) / Eo) * Pmp0 * (1 + g * (Tm - To))) * derating_factor

        if p < 1:
            p = 0

        # System losses and performance ratio adjustments
        s1 = (100 - system_losses) / 100
        s2 = 1 - ((100 - performance_ratio) / 100)

        # Calculate energy output
        energy = panel_size * p * s1 * s2

        return energy

    def compute_predictions(self, X_test: pd.DataFrame) -> pd.DataFrame:
        return X_test.apply(lambda x: self.calculate_energy(
            x["direct_normal_irradiance"], x["diffuse_radiation"],
            x["shortwave_radiation"], x["zenith"],
            x["azimuth"], x["temperature_2m"],
            **self.params
        ), axis=1)


    def retrieve_model(self):
        pass