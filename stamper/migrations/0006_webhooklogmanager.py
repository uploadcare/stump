# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-23 22:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stamper', '0005_failedtask'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookLogManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
