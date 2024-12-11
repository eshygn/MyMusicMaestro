from django.shortcuts import render, get_object_or_404, redirect
from .models import Album, AlbumTracklistItem, MusicManagerUser, Song
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .forms import AlbumForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

@login_required
def album_list(request):
    user = request.user
    try:
        user_profile = user.musicmanageruser  
        if user_profile.user_type == 'artist':
            albums = Album.objects.filter(artist=user_profile.display_name)
        else:
            albums = Album.objects.all()

    except MusicManagerUser.DoesNotExist:
        albums = Album.objects.none()
    return render(request, 'label_music_manager/album_list.html', {'albums': albums})

@login_required
def album_detail(request, id):
    album = get_object_or_404(Album, id=id)
    if request.user.musicmanageruser.user_type == 'artist' and album.artist != request.user.musicmanageruser.display_name:
        messages.error(request, "You are not allowed to view this album.")
        return redirect('album-list')
    return render(request, 'label_music_manager/album_detail.html', {'album': album})

@login_required
def album_create(request):
    user = request.user
    try:
        user_profile = user.musicmanageruser
        if user_profile.user_type == 'artist' or user_profile.user_type == 'editor':
            if request.method == 'POST':
                form = AlbumForm(request.POST, request.FILES)
                if form.is_valid():
                    # Save the album first (commit=False to prevent saving it right now)
                    album = form.save(commit=False)

                    # Assign artist if the user is an artist
                    if user_profile.user_type == 'artist':
                        album.artist = user_profile.display_name  # Assign artist from user profile
                    
                    # Save the album now to get the ID
                    album.save()

                    # Add songs to album through the tracklist (via AlbumTracklistItem)
                    tracklist_data = request.POST.getlist('tracklist')  # Get the list of song IDs
                    for position, song_id in enumerate(tracklist_data, 1):
                        song = Song.objects.get(id=song_id)
                        AlbumTracklistItem.objects.create(album=album, song=song, position=position)

                    messages.success(request, "Album created successfully!")
                    return redirect('album-list')
            else:
                form = AlbumForm()
            return render(request, 'label_music_manager/album_form.html', {'form': form})
        else:
            messages.error(request, "You do not have permission to create an album.")
            return redirect('album-list')
    except MusicManagerUser.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('album-list')
    
@login_required
def album_edit(request, id):
    album = get_object_or_404(Album, id=id)
    if (request.user.musicmanageruser.user_type == 'artist' and album.artist != request.user.musicmanageruser.display_name) or request.user.musicmanageruser.user_type == 'viewer':
        messages.error(request, "You do not have permission to edit this album.")
        return redirect('album-list')

    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            album = form.save()  
            tracklist_data = form.cleaned_data['tracklist']  
            album.songs.clear()
            
            for song in tracklist_data:
                AlbumTracklistItem.objects.create(album=album, song=song)
            
            messages.success(request, "Album updated successfully!")
            return redirect('album-detail', id=id)
    else:
        form = AlbumForm(instance=album)
    
    return render(request, 'label_music_manager/album_form.html', {'form': form})

@login_required
def album_delete(request, id):
    album = get_object_or_404(Album, id=id)
    
    if (request.user.musicmanageruser.user_type == 'artist' and album.artist != request.user.musicmanageruser.display_name) or request.user.musicmanageruser.user_type == 'viewer':
        messages.error(request, "You do not have permission to delete this album.")
        return redirect('album-list')

    if request.method == 'POST':  
        album.delete()
        messages.success(request, "Album deleted successfully.")
        return redirect('album-list')
    
    return render(request, 'label_music_manager/album_confirm_delete.html', {'album': album})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'album-list')  
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_logout(request):
    if request.method == 'POST':  
        logout(request) 
        return redirect('login')
    return redirect('album-list')

@login_required
def album_detail_slug(request, id, slug):
    album = get_object_or_404(Album, id=id)
    
    if album.slug != slug:
        return redirect('album-detail-slug', id=id, slug=album.slug)

    return render(request, 'label_music_manager/album_detail.html', {'album': album})