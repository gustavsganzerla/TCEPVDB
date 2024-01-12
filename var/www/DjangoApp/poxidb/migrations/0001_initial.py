# Generated by Django 4.2.4 on 2024-01-12 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Epitope",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("description", models.CharField(max_length=1000)),
                ("sequence", models.CharField(max_length=50)),
                ("epitope_score", models.FloatField()),
                ("organism", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Proteome",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("description", models.CharField(max_length=1000)),
                ("protein", models.CharField(max_length=10000)),
                ("organism", models.CharField(max_length=100)),
                ("antigen", models.CharField(max_length=50)),
                ("antigen_score", models.FloatField()),
            ],
        ),
    ]
