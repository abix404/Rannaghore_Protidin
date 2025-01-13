# Generated by Django 5.1.4 on 2025-01-13 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=15)),
                ('last_name', models.CharField(max_length=15)),
                ('mobile_no', models.IntegerField(max_length=14)),
                ('email', models.EmailField(max_length=254)),
                ('bio', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
