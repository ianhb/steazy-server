from django.conf.urls import url, patterns
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as auth

import views

__author__ = 'Ian'

urlpatterns = patterns('',
                       url(r'^login/$', auth.obtain_auth_token),
                       url(r'^songs/$', views.SongsList.as_view()),
                       url(r'^songs/fast/$', views.FastSongSearch.as_view()),
                       url(r'^playlists/$', views.PlaylistList.as_view()),
                       url(r'^playlists/(?P<pk>[0-9]+)/$', views.PlaylistDetail.as_view()),
                       url(r'^users/$', views.UserView.as_view()),
                       url(r'^users/create/$', views.CreateUser.as_view()),

                       url(r'^play/$', views.PlayView.as_view()),
                       url(r'^add/$', views.AddToPlaylistView.as_view()),
                       )

urlpatterns = format_suffix_patterns(urlpatterns)
