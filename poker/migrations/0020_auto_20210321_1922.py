# Generated by Django 3.1.6 on 2021-03-21 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poker', '0019_auto_20210315_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokertable',
            name='player_0',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='pokertable',
            name='player_1',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='pokertable',
            name='player_2',
            field=models.CharField(max_length=64, null=True),
        ),
    ]