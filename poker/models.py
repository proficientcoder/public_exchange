from django.db import models
from django.contrib.auth.models import User


class PokerTable(models.Model):
    size = models.IntegerField()
    player_1 = models.ForeignKey(User, related_name='user_1', on_delete=models.CASCADE, null=True)
    player_2 = models.ForeignKey(User, related_name='user_2', on_delete=models.CASCADE, null=True)
