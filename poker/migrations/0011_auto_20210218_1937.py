# Generated by Django 3.1.6 on 2021-02-18 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poker', '0010_pokertable_blind'),
    ]

    operations = [
        migrations.AddField(
            model_name='pokertable',
            name='last_to_act',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokertable',
            name='next_to_act',
            field=models.IntegerField(default=0),
        ),
    ]
