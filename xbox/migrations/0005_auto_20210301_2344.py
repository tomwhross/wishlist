# Generated by Django 3.1.7 on 2021-03-01 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xbox', '0004_game_current_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='noted_sale',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='noted_sale_type',
            field=models.TextField(blank=True, default=None, max_length=255, null=True),
        ),
    ]