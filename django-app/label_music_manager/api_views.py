# Use this file for your API viewsets only
# E.g., from rest_framework import ...
from rest_framework import viewsets
from .models import Album, AlbumTracklistItem, Song
from .serializers import AlbumSerializer, AlbumTracklistItemSerializer, SongSerializer

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class AlbumTracklistItemViewSet(viewsets.ModelViewSet):
    queryset = AlbumTracklistItem.objects.all()
    serializer_class = AlbumTracklistItemSerializer

    