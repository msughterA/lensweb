# Generated by Django 4.0 on 2021-12-12 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=500)),
                ('embedding', models.TextField(max_length=2000)),
                ('exam', models.TextField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Diagram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('base64string', models.TextField(max_length=300)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='examples.question')),
            ],
        ),
    ]
