# Generated by Django 3.1.6 on 2021-03-29 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poker', '0020_auto_20210321_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='pokertable',
            name='player_3',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_3_action',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_3_cards',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_3_join',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_3_leave',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_3_money',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_3_new_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_3_prev_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_4',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_4_action',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_4_cards',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_4_join',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_4_leave',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_4_money',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_4_new_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_4_prev_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_5',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_5_action',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_5_cards',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_5_join',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_5_leave',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_5_money',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_5_new_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_5_prev_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_6',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_6_action',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_6_cards',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_6_join',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_6_leave',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_6_money',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_6_new_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_6_prev_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_7',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_7_action',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_7_cards',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_7_join',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_7_leave',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_7_money',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_7_new_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_7_prev_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_8',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_8_action',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_8_cards',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_8_join',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_8_leave',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_8_money',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_8_new_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_8_prev_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_9',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_9_action',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_9_cards',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_9_join',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_9_leave',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_9_money',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_9_new_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='player_9_prev_bet',
            field=models.IntegerField(default=0),
        ),
    ]
