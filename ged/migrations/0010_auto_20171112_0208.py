# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-12 05:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ged', '0009_remove_tipodocumento_tipo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tipo',
            name='tipo',
        ),
        migrations.AddField(
            model_name='tipo',
            name='pasta',
            field=models.CharField(default='', max_length=200, verbose_name='Nome'),
            preserve_default=False,
        ),
    ]
