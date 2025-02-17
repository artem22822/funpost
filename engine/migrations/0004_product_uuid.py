# Generated by Django 4.2.4 on 2024-09-30 15:14

from django.db import migrations, models
import engine.models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0003_alter_address_phone_number_alter_order_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='uuid',
            field=models.CharField(default=engine.models.uuid, editable=False, max_length=64, unique=True),
        ),
    ]
