# Use this file for your templated views only

from django.db import models
from django.contrib.auth.models import User

class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    @property
    def short_description(self):
        return self.description[:255] + '…' if len(self.description) > 255 else self.description
    
    @property
    def release_year(self):
        return self.release_date.year
    
    @property
    def total_playtime(self):
        return sum(song.length for song in self.tracklist.all())

class Song(models.Model):
    title = models.CharField(max_length=255)
    length = models.IntegerField()  

class Tracklist(models.Model):
    album = models.ForeignKey(Album, related_name='tracklist', on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    position = models.IntegerField()