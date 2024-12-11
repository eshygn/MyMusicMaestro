from django import forms
from .models import Album, Song
from django.contrib.auth.models import User


class AlbumForm(forms.ModelForm):
    tracklist = forms.ModelMultipleChoiceField(queryset=Song.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    
    class Meta:
        model = Album
        fields = ['title', 'description', 'artist', 'price', 'format', 'release_date', 'cover_image', 'tracklist']
        
    release_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
    )

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)