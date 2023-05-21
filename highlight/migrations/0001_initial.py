# Generated by Django 4.1.9 on 2023-05-21 17:06

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Highlight',
            fields=[
                ('token', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('link', models.CharField(max_length=255)),
                ('progress', models.IntegerField(default=0)),
                ('highlight_link', models.CharField(max_length=255, null=True)),
                ('timestamp', models.JSONField()),
            ],
        ),
    ]