# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-08 16:58
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stamper', '0003_auto_20161122_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileuploadmessage',
            name='original_file_url',
            field=models.CharField(default=datetime.datetime(2016, 12, 8, 16, 57, 50, 623808, tzinfo=utc), max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='imageuploadmessage',
            name='original_file_url',
            field=models.CharField(default=datetime.datetime(2016, 12, 8, 16, 58, 2, 437475, tzinfo=utc), max_length=255),
            preserve_default=False,
        ),
    ]