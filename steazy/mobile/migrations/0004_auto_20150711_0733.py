# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('mobile', '0003_spotifyuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotifyuser',
            name='authorization_code',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='spotifyuser',
            name='refresh_token',
            field=models.TextField(),
        ),
    ]
