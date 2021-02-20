from django.db import models
from django.contrib.auth.models import User



class apiKey(models.Model):
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    key = models.CharField(max_length=50)
