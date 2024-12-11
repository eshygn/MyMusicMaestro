# Write your models here
from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta

class Album(models.Model):
    title=models.CharField(max_length=512, unique=True)
    description=models.TextField(blank=True)
    artist=models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2, validators=[
        MinValueValidator(0),
        MaxValueValidator(999.99)
    ])
    FORMAT_CHOICES = [
        ('DD', 'Digital Download'),
        ('CD', 'CD'),
        ('VL' ,'Vinyl'),
    ]
    format = models.CharField(max_length=2, choices=FORMAT_CHOICES)
    release_date=models.DateField()
    cover_image = models.ImageField(
        default='covers/default.jpg',
        blank = True,
        null = True
    )
    slug = models.SlugField(
        unique = True, 
        editable = False,
    )
    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.title}-{self.format}")
        super().save(*args, **kwargs)
    def clean(self): 
        if self.release_date>date.today() + timedelta(days = 3*365):
            raise ValidationError("Release date cannot be more than 3 years in the future")
    def __str__(self):
        return f"{self.title} by {self.artist}"
    
class Song(models.Model):
    title = models.CharField(max_length=512)
    length = models.PositiveBigIntegerField(validators =  [MinValueValidator(10)])
    albums = models.ManyToManyField(
        'Album', through = 'AlbumTracklistItem',
        related_name='songs'
    )
    def __str__(self):
        return self.title
    
class AlbumTracklistItem(models.Model):
    song = models.ForeignKey(Song, on_delete = models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(null = True, blank = True)
    class Meta:
        unique_together = ('album', 'song')

    def __str__(self):
        return f"{self.song.title} in {self.album.title} (Track {self.position})"
    
class MusicManagerUser(models.Model):
    USER_TYPE_CHOICES = [
        ('artist', 'Artist'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]

    user = models.OneToOneField('auth.User', on_delete = models.CASCADE)
    display_name = models.CharField(max_length = 512)
    user_type = models.CharField(max_length = 10, choices=USER_TYPE_CHOICES)
    
    def __str__(self):
        return self.display_name
