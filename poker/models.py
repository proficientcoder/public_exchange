from django.db import models
from django.contrib.auth.models import User



class PokerTable(models.Model):
    size = models.IntegerField()
    state = models.IntegerField(default=0)
    dealer = models.IntegerField(default=0)
    next_to_act = models.IntegerField(default=0)
    last_to_act = models.IntegerField(default=0)
    blind = models.DecimalField(max_digits=18, decimal_places=2, default=1)
    deck = models.CharField(max_length=52, null=True)
    pot = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    board = models.CharField(max_length=10, null=True)
    showDownCounter = models.DateTimeField(null=True)
    player_1 = models.ForeignKey(User, related_name='user_1', on_delete=models.CASCADE, null=True)
    player_1_cards = models.CharField(max_length=4, null=True)
    player_1_bet = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    player_1_money = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    player_2 = models.ForeignKey(User, related_name='user_2', on_delete=models.CASCADE, null=True)
    player_2_cards = models.CharField(max_length=4, null=True)
    player_2_bet = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    player_2_money = models.DecimalField(max_digits=18, decimal_places=2, default=0)
