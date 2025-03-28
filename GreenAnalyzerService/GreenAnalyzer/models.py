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

    METRIC_CHOICES = [
        ('MAE', 'MAE'),
        ('MSE', 'MSE'),
        ('RMSE', 'RMSE'),
        ('R2', 'R2'),
        ('RMSLE', 'RMSLE'),
        ('MAPE', 'MAPE'),
        ('SMAPE', 'SMAPE')
    ]

        # identity = 1
        # id_provided = True

        # date_col = 'date'
        # pv_col = 'inverter1'

        # latitude = 35.1542
        # longitude = 33.3964
        # timezone = 'Europe/Moscow'

        # model_type = 'Naive' #['AI','Naive','Math']

        # panel_tilt = 17
        # panel_size = 63*1.7*1
        # n_trials = 100

        # optimize_metric = 'MAPE'

    name = models.CharField(max_length=100, unique=True, primary_key=True)
    res_type = models.CharField(max_length=100, choices=STATUS_CHOICES)
    # days_of_prediction = models.IntegerField(default=2)
    lat = models.FloatField()
    lon = models.FloatField()
    timezone = models.CharField(max_length=100, default='Europe/Athens')
    model_type = models.CharField(max_length=100, choices=MODEL_CHOICES)
    optimize_metric = models.CharField(max_length=100, choices=METRIC_CHOICES, default='MAPE')
    n_trials = models.IntegerField(default=100)

    date_col = models.CharField(max_length=100, default='date')
    energy_col = models.CharField(max_length=100, default='energy')
    panel_tilt = models.FloatField(default=20)
    panel_size = models.FloatField(default=10)

    parameters = models.JSONField(default=None, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    stored_model = models.FileField(upload_to='energy_pv_models', default=None)

    csv_file = models.FileField(upload_to='dfs', default=None)

    def get_model_path(self):
        if self.stored_model:
            return self.stored_model.name.replace('.pkl', '') # self.stored_model.path.replace('.pkl', '')

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
