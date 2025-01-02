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

model_mapping = dict(AI=AIModel, NAIVE=NaiveModel, MATH=MathModel)


class RESViewSet(viewsets.ModelViewSet):
    queryset = RESModel.objects.all()
    serializer_class = RESSerializer

    @action(detail=True, methods=['get'], name="predict_res")
    def predict(self, request, pk=None):
        res_model: RESModel = self.get_object()
        horizon = request.data.get('horizon', 7)

        lat = request.data.get("latitude")
        lon = request.data.get("longitude")

        # Retrieve Weather Data
        if lat and lon:
            X_test = WeatherService().get_weather_forecast(float(lat), float(lon), forecast_days=horizon)
        else:
            X_test = WeatherService().get_weather_forecast(res_model.lat, res_model.lon, forecast_days=horizon)

        ModelClass = model_mapping.get(res_model.model_type)

        if ModelClass is None:
            raise Http404

        stored_model_path = res_model.get_model_path()

        model_handler = ModelClass(stored_model_path, params=res_model.parameters)
        model_handler.retrieve_model()

        # Make the prediction
        output = model_handler.compute_predictions(X_test)

        X_test['prediction'] = output
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
