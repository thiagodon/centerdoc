# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-03 13:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ged', '0005_documento_pagina'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagina',
            name='nomes',
            field=models.CharField(default='', max_length=1000, verbose_name='Nomes Citados'),
            preserve_default=False,
        ),
    ]
