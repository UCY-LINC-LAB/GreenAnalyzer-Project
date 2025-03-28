import os

from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from services.carbon_emission_service import get_carbon_footprint
from services.energy_mix_service import CountryEnergyMix
from services.rest_europe_energy_mix_service import RestEuropeEnergyMixService
from services.weather import WeatherService
from .models import RESModel, EnergyProfile

from .serializers import RESSerializer, EnergyProfileSerializer
from services.modeler import AIModel, NaiveModel, MathModel
from services.preprocessing_and_training import preprocessing_and_training
from django.core.files.storage import default_storage

model_mapping = dict(AI=AIModel, NAIVE=NaiveModel, MATH=MathModel)


class RESViewSet(viewsets.ModelViewSet):
    queryset = RESModel.objects.none()  # to not print/show all the items of the database
    #queryset = RESModel.objects.all()
    serializer_class = RESSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        # preprocessing_and_training(serializer, default_storage.path(instance.csv_file.name))
        preprocessing_and_training(instance)
        # parameters_and_model = training(serializer.validated_data['name'], serializer.validated_data['date_col'], serializer.validated_data['energy_col'], 
        #                                 serializer.validated_data['lat'], serializer.validated_data['lon'], serializer.validated_data['timezone'], 
        #                                 serializer.validated_data['model_type'], serializer.validated_data['panel_tilt'], serializer.validated_data['panel_size'], 
        #                                 serializer.validated_data['n_trials'], serializer.validated_data['optimize_metric'], instance.csv_file.name)
        # serializer.save(parameters = parameters_and_model[0])
        # serializer.save(stored_model = parameters_and_model[1])


    @action(detail=True, methods=['get'], name="predict_res")
    def predict(self, request, pk=None):
        # res_model: RESModel = self.get_object()
        
        item = RESModel.objects.get(pk=pk)
        
        horizon = request.query_params.get('horizon', 7)

        lat = request.query_params.get("latitude")
        lon = request.query_params.get("longitude")

        # Retrieve Weather Data
        if lat and lon:
            X_test = WeatherService().get_weather_forecast(float(lat), float(lon), forecast_days=horizon)
        else:
            X_test = WeatherService().get_weather_forecast(item.lat, item.lon, forecast_days=horizon)
 
        ModelClass = model_mapping.get(item.model_type)

        if ModelClass is None:
            raise Http404
        
        fields = sorted(['apparent_temperature', 'cloud_cover', 
           'cloud_cover_high', 'cloud_cover_low', 'cloud_cover_mid',
           'diffuse_radiation', 'diffuse_radiation_instant',
           'direct_normal_irradiance', 'direct_normal_irradiance_instant',
           'direct_radiation', 'direct_radiation_instant',
           'global_tilted_irradiance', 'is_day', 'precipitation', 'pressure_msl',
           'rain', 'relative_humidity_2m', 'shortwave_radiation',
           'shortwave_radiation_instant', 'sunshine_duration', 'surface_pressure',
           'temperature_2m', 'terrestrial_radiation',
           'terrestrial_radiation_instant', 'wind_direction_100m',
           'wind_direction_10m', 'wind_gusts_10m', 'wind_speed_100m',
           'wind_speed_10m', 'azimuth', 'zenith', 'dusk', 'dawn', 'elevation',
           'golden_hour_start', 'golden_hour_end', 'month', 'hour'])
        
        model_handler = ModelClass(item.get_model_path(), params=item.parameters)
        model_handler.retrieve_model()

        # Make the prediction
        output = model_handler.compute_predictions(X_test[fields])

        X_test['prediction'] = output
        X_test['prediction'] = X_test.apply(lambda x: 0 if x['shortwave_radiation']==0 else x['prediction'],axis=1)
        data = X_test[['date', 'prediction']].to_dict('records')

        return Response(data, status=status.HTTP_200_OK)


class EnergyProfileView(viewsets.ModelViewSet):
    queryset = EnergyProfile.objects.all()
    serializer_class = EnergyProfileSerializer

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def predict_country_energy_mix(request):
    country = request.data.get("country", "POLAND")

    if country in ["POLAND", "CYPRUS"]:
        cem = CountryEnergyMix(country)
    else:
        cem = RestEuropeEnergyMixService(api_key=os.getenv("ENTSOE_API_KEY"), country=country)

    pv, wind, total = cem.predict_mix()
    pv = pv.reset_index()
    pv, wind, total = update_output(pv, total, wind)
    gCO2eq_footprint_per_KWh = get_carbon_footprint(pv, wind, total, country)

    return Response({"pv": pv.to_dict("records"),
                     "wind": wind.to_dict("records"),
                     "total": total.to_dict("records"),
                     "carbon_intensity": gCO2eq_footprint_per_KWh.to_dict("records")})


def update_output(pv, total, wind):
    if "predictions_pv" in pv.columns:
        pv["pred"] = pv["predictions_pv"]
        del pv["predictions_pv"]
    if "pv" in pv.columns:
        pv["pred"] = pv["pv"]
        del pv["pv"]
    wind = wind.reset_index()
    if "wind" in wind.columns:
        wind["pred"] = wind["wind"]
        del wind["wind"]
    total = total.reset_index()
    if "total" in total.columns:
        total["pred"] = total["total"]
        del total["total"]
    return pv, wind, total
