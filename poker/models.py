from django.db import models
from django.contrib.auth.models import User



class PokerTable(models.Model):
    size = models.IntegerField()
    state = models.IntegerField(default=0)
    dealer = models.IntegerField(default=0)
    next_to_act = models.IntegerField(default=0)
    last_to_act = models.IntegerField(default=0)
    blind = models.IntegerField(default=0)
    deck = models.CharField(max_length=52, null=True)
    board = models.CharField(max_length=10, null=True)
    eventTimer = models.DateTimeField(null=True)
    updateTimer = models.DateTimeField(null=True)
    player_0 = models.ForeignKey(User, related_name='user_0', on_delete=models.CASCADE, null=True)
    player_0_cards = models.CharField(max_length=4, null=True)
    player_0_new_bet = models.IntegerField(default=0)
    player_0_prev_bet = models.IntegerField(default=0)
    player_0_money = models.IntegerField(default=0)
    player_0_action = models.BooleanField(default=False)
    player_1 = models.ForeignKey(User, related_name='user_1', on_delete=models.CASCADE, null=True)
    player_1_cards = models.CharField(max_length=4, null=True)
    player_1_new_bet = models.IntegerField(default=0)
    player_1_prev_bet = models.IntegerField(default=0)
    player_1_money = models.IntegerField(default=0)
    player_1_action = models.BooleanField(default=False)
    player_2 = models.ForeignKey(User, related_name='user_2', on_delete=models.CASCADE, null=True)
    player_2_cards = models.CharField(max_length=4, null=True)
    player_2_new_bet = models.IntegerField(default=0)
    player_2_prev_bet = models.IntegerField(default=0)
    player_2_money = models.IntegerField(default=0)
    player_2_action = models.BooleanField(default=False)
