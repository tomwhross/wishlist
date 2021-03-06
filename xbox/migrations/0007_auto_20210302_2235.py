# Generated by Django 3.1.7 on 2021-03-02 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xbox', '0006_gamepricehistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamepricehistory',
            name='noted_sale',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gamepricehistory',
            name='noted_sale_type',
            field=models.TextField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
