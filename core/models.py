from django.db import models
from django.contrib.auth.models import User


# Create your models here.
legal_forms = (
    (1, 'Currency'),
)

class Contract(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    descriptive_name = models.CharField(max_length=32, unique=True)
    legal = models.IntegerField(choices=legal_forms, default=1)
    unique = models.BooleanField(default=True)
    expandable = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    website = models.CharField(max_length=512)
    expiry_date = models.DateTimeField()
    underlying_value = models.TextField()

