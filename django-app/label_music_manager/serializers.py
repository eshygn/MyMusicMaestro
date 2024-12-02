from rest_framework import serializers
from .models import Album, Song, AlbumTracklistItem

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'title', 'length']

class AlbumSerializer(serializers.ModelSerializer):
    tracks = SongSerializer(source='songs', many=True, read_only=True) 

    class Meta:
        model = Album
        fields = ['id', 'title', 'description', 'artist', 'price', 'format', 'release_date', 'cover_image', 'slug', 'tracks']