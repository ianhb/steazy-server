from django.contrib import admin

# Register your models here.
from models import Song, Playlist, Search, SpotifyUser

class PlaylistAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'owner', 'songs']}),
    ]

admin.site.register(Song)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Search)
admin.site.register(SpotifyUser)
