from datetime import timezone

from django.db import models


class RESModel(models.Model):
    STATUS_CHOICES = [
        ('PV', 'PV'),
        ('WIND', 'WIND'),
    ]

    MODEL_CHOICES = [
        ('AI', 'AI'),
        ('NAIVE', 'NAIVE'),
        ('MATH', 'MATH')
    ]

    name = models.CharField(max_length=100, unique=True, primary_key=True)
    res_type = models.CharField(max_length=100, choices=STATUS_CHOICES)
    lat = models.FloatField()
    lon = models.FloatField()
    model_type = models.CharField(max_length=100, choices=MODEL_CHOICES)
    parameters = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    stored_model = models.FileField(upload_to='energy_pv_models', default=None)

    def get_model_path(self):
        if self.stored_model:
            return self.stored_model.path.replace('.pkl', '')

class EnergyProfile(models.Model):
    name = models.CharField(max_length=100, unique=True, primary_key=True)
    dynamic = models.FloatField()
    static = models.FloatField()


# class CountryEnergyMix(models.Model):
#     COUNTRY_CHOICES = [
#         ('CYPRUS', 'CYPRUS'),
#         ('POLAND', 'POLAND'),]
#
#     RES_LOCATIONS = {
#         'CYPRUS': {
#             'wind': [(34.8694, 33.5168), (34.9609, 33.4916), (34.7394, 32.6574)],
#             'pv': [(35.1542, 33.3964), (34.7404, 32.5336), (34.6025, 32.9776)],
#             'cities': [(35.1856, 33.3823), (34.6786, 33.0413), (34.7754, 32.4218)],
#         }
#     }
#
#     country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, primary_key=True)
#     stored_model = models.FileField(upload_to='energy_mix_models/forecast')
