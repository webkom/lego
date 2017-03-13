# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-11 22:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0007_auto_20170311_0035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinterest',
            name='comment',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='companyinterest',
            name='events',
            field=models.CommaSeparatedIntegerField(blank=True, choices=[(0, 'Company presentation'), (1, 'Course'), (3, 'Lunch presentation'), (5, 'Bedex'), (4, 'Jubileum'), (2, 'Other')], max_length=30),
        ),
        migrations.AlterField(
            model_name='companyinterest',
            name='semesters',
            field=models.ManyToManyField(blank=True, to='companies.Semester'),
        ),
    ]
