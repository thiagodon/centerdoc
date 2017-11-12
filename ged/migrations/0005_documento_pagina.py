# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-20 02:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ged', '0004_auto_20171018_0119'),
    ]

    operations = [
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('nomes', models.CharField(max_length=1000, verbose_name='Nomes Citados')),
                ('informacoes', models.TextField(verbose_name='Informações')),
                ('palavras_chave', models.CharField(max_length=200, verbose_name='Palavras Chave')),
                ('texto', models.TextField(verbose_name='Texto')),
                ('paginas', models.IntegerField(verbose_name='Quantidade de Páginas')),
                ('ano', models.IntegerField(verbose_name='Ano')),
                ('removido', models.BooleanField(default=False)),
                ('user_add', models.IntegerField()),
                ('date_add', models.DateField()),
                ('user_up', models.IntegerField(blank=True, null=True)),
                ('date_up', models.DateField(blank=True, null=True)),
                ('user_del', models.IntegerField(blank=True, null=True)),
                ('date_del', models.DateField(blank=True, null=True)),
                ('tipo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documento_tipo', to='ged.Tipo', verbose_name='Tipo')),
            ],
        ),
        migrations.CreateModel(
            name='Pagina',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('palavras_chave', models.CharField(max_length=200, verbose_name='Palavras chave')),
                ('pagina', models.IntegerField(verbose_name='Página número')),
                ('arquivo', models.FileField(upload_to='')),
                ('informacoes', models.TextField(verbose_name='Informaçẽos')),
                ('inicio', models.TextField(verbose_name='Inicia com')),
                ('fim', models.TextField(verbose_name='Termina com')),
                ('removido', models.BooleanField(default=False)),
                ('user_add', models.IntegerField()),
                ('date_add', models.DateField()),
                ('user_up', models.IntegerField(blank=True, null=True)),
                ('date_up', models.DateField(blank=True, null=True)),
                ('user_del', models.IntegerField(blank=True, null=True)),
                ('date_del', models.DateField(blank=True, null=True)),
                ('documento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documento_paginas', to='ged.Documento', verbose_name='Documento')),
                ('tipo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagina_tipo', to='ged.Tipo', verbose_name='Tipo')),
            ],
        ),
    ]