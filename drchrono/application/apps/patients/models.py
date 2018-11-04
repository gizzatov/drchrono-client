from django.db import models
from model_utils.models import TimeStampedModel


class Patient(TimeStampedModel):
    user = models.ManyToManyField('auth.User', related_name='patients')
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    birth_date = models.DateField(null=True)
    phone_number = models.CharField(max_length=250, blank=True)
    photo = models.CharField(max_length=500, null=True)
    internal_id = models.CharField(max_length=100, unique=True)  # patient's ID on provider
    internal_updated_at = models.CharField(max_length=100)  # patient's updated_at on provider

    def __str__(self):
        return self.internal_id
