from django.db import models
from django.contrib.auth.models import User


# Create your models here.
legal_forms = [
    ('CURRENCY', 'CURRENCY'),
    ('SHARES', 'SHARES'),
]


class User_details(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    email = models.CharField(max_length=512)
    email_verified = models.BooleanField(default=False)
    website = models.CharField(max_length=512)


class Contract(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    descriptive_name = models.CharField(max_length=32, unique=True)
    legal = models.CharField(max_length=16, choices=legal_forms)
    unique = models.BooleanField(default=True)
    expandable = models.BooleanField(default=False)
    allow_fractions = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    website = models.CharField(max_length=512)
    expiry_date = models.DateTimeField()
    details = models.TextField()


class Ownership(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, default=1)
    created_by = models.ForeignKey(User, related_name='create_by', on_delete=models.CASCADE, default=1)
    owned_by = models.ForeignKey(User, related_name='owned_by', on_delete=models.CASCADE, default=1)
    amount = models.IntegerField(default=1)


