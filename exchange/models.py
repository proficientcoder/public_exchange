from django.db import models
from django.contrib.auth.models import User


class Ticker(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, unique=True)


class Ownership(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, related_name='creator', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE)
    amount = models.IntegerField()
