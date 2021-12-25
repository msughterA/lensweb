# Generated by Django 4.0 on 2021-12-22 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20, null=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=8)),
                ('device_id', models.CharField(blank=True, max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=8)),
                ('isActive', models.BooleanField(default=True)),
                ('device_id', models.CharField(max_length=20)),
                ('login_at', models.DateTimeField(auto_now_add=True)),
                ('account_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='accounts.account')),
            ],
        ),
    ]
