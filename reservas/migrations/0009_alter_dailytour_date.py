# Generated by Django 5.1.1 on 2024-10-10 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0008_alter_tour_activation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailytour',
            name='date',
            field=models.DateField(),
        ),
    ]