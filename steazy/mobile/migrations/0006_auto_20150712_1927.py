# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('mobile', '0005_auto_20150712_1830'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song_to_playlist',
            name='added_by',
        ),
        migrations.RemoveField(
            model_name='song_to_playlist',
            name='playlist',
        ),
        migrations.RemoveField(
            model_name='song_to_playlist',
            name='song',
        ),
        migrations.AddField(
            model_name='playlist',
            name='songs',
            field=models.ManyToManyField(to='mobile.Song'),
        ),
        migrations.DeleteModel(
            name='Song_to_Playlist',
        ),
    ]
