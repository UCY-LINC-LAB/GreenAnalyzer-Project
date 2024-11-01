import pandas as pd
import pycountry

countries = {}
for country in pycountry.countries:
    countries[country.name.upper()] = country.alpha_2

emissions_df = pd.read_csv('services/ElectricityMapsEmissionFactors.csv')


def get_carbon_footprint(pv, wind, total, country, emission_type="lifecycle") -> pd.DataFrame:
    country_code = countries.get(country)
    if country_code is None:
        raise Exception("Unknown country")
    df = emissions_df[
        (emissions_df["zone_key"] == country_code) & (emissions_df['emission_factor_type'] == emission_type)]
    wind_parameter = df[df.production_mode == "wind"].iloc[0].value
    solar_parameter = df[df.production_mode == "solar"].iloc[0].value
    oil_parameter = df[df.production_mode == "oil"].iloc[0].value
    print(total)
    print(pv)
    print(wind)
    oil = total.reset_index().pred - pv.reset_index().pred - wind.reset_index().pred
    gCO2eq_footprint_per_KWh = solar_parameter * pv.reset_index().pred + wind_parameter * wind.reset_index().pred + oil_parameter * oil
    return pd.DataFrame({"pred": gCO2eq_footprint_per_KWh})
