from django.db import models
from django.contrib.auth.models import User


class Ticker(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, unique=True)


class Ownership(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    holder = models.ForeignKey(User, related_name='holder', on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE)
    amount = models.IntegerField()
