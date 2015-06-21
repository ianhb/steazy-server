# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Play',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('artist', models.CharField(max_length=255)),
                ('album', models.CharField(max_length=255)),
                ('source', models.CharField(max_length=20, choices=[(b'Spotify', b'SPO'), (b'Soundcloud', b'SOU')])),
                ('tag', models.CharField(max_length=30)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('plays', models.IntegerField(default=0)),
                ('inherited_popularity', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Song_to_Playlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('playlist', models.ForeignKey(to='mobile.Playlist')),
                ('song', models.ForeignKey(to='mobile.Song')),
            ],
        ),
        migrations.AddField(
            model_name='play',
            name='song',
            field=models.ForeignKey(to='mobile.Song'),
        ),
    ]
