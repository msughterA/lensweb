# Generated by Django 4.1.4 on 2022-12-26 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_alter_login_device_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="password",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="login",
            name="password",
            field=models.CharField(max_length=20),
        ),
    ]