from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError  # Added import for ValidationError
from datetime import date, timedelta
from .models import Album, Song, AlbumTracklistItem, MusicManagerUser
from .forms import AlbumForm
from django.test import override_settings

class ModelTests(TestCase):
    def setUp(self):
        # Create a test user and profile
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_profile = MusicManagerUser.objects.create(
            user=self.user,
            display_name='Test Artist',
            user_type='artist'
        )

    def test_album_creation(self):
        # Test creating a valid album
        album = Album.objects.create(
            title='Test Album',
            artist='Test Artist',
            price=9.99,
            format='DD',
            release_date=date.today()
        )
        
        self.assertEqual(album.title, 'Test Album')
        self.assertEqual(album.slug, 'test-album-dd')
        self.assertEqual(str(album), 'Test Album by Test Artist')

    def test_album_future_date_validation(self):
        # Test validation for release date > 3 years 
        with self.assertRaises(ValidationError):
            album = Album(
                title='Future Album',
                artist='Test Artist',
                price=9.99,
                format='CD',
                release_date=date.today() + timedelta(days=1100)
            )
            album.full_clean()  # This will raise ValidationError

    def test_song_creation(self):
        # Test creating a song
        song = Song.objects.create(
            title='Test Song',
            length=180  # 3 minutes
        )
        
        self.assertEqual(song.title, 'Test Song')
        self.assertEqual(str(song), 'Test Song')

    def test_album_tracklist_item(self):
        # Test creating an album tracklist 
        album = Album.objects.create(
            title='Test Album',
            artist='Test Artist',
            price=9.99,
            format='DD',
            release_date=date.today()
        )
        song = Song.objects.create(
            title='Test Song',
            length=180
        )
        
        tracklist_item = AlbumTracklistItem.objects.create(
            album=album,
            song=song,
            position=1
        )
        
        self.assertEqual(str(tracklist_item), 'Test Song in Test Album (Track 1)')

class ViewTests(TestCase):
    def setUp(self):
        # Test with creating users with different portfolio
        self.artist_user = User.objects.create_user(username='artist', password='12345')
        self.artist_profile = MusicManagerUser.objects.create(
            user=self.artist_user,
            display_name='Artist Name',
            user_type='artist'
        )

        self.editor_user = User.objects.create_user(username='editor', password='54321')
        self.editor_profile = MusicManagerUser.objects.create(
            user=self.editor_user,
            display_name='Editor Name',
            user_type='editor'
        )

        self.viewer_user = User.objects.create_user(username='viewer', password='67890')
        self.viewer_profile = MusicManagerUser.objects.create(
            user=self.viewer_user,
            display_name='Viewer Name',
            user_type='viewer'
        )

        # Test album creation
        self.test_album = Album.objects.create(
            title='Test Album',
            artist='Artist Name',
            price=9.99,
            format='DD',
            release_date=date.today()
        )

    def test_album_list_view_artist(self):
        # Test album list view for artist
        self.client.login(username='artist', password='12345')
        response = self.client.get(reverse('album-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Album')

    def test_album_create_view_permissions(self):
        # Test album creation permissions
        # Check if artist can create 
        self.client.login(username='artist', password='12345')
        album_data = {
            'title': 'New Artist Album',
            'price': 9.99,
            'format': 'CD',
            'release_date': date.today(),
            'tracklist': [] 
        }
        response = self.client.post(reverse('album-create'), data=album_data)
        self.assertIn(response.status_code, [200, 302])  

        # Can viewer create 
        self.client.login(username='viewer', password='67890')
        response = self.client.post(reverse('album-create'), data=album_data)
        self.assertRedirects(response, reverse('album-list'))

    def test_album_edit_view_permissions(self):
        # Test if artists can edit their own albums
        self.client.login(username='artist', password='12345')
        edit_url = reverse('album-edit', args=[self.test_album.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)

        # Viewer cannot edit
        self.client.login(username='viewer', password='67890')
        response = self.client.get(edit_url)
        self.assertRedirects(response, reverse('album-list'))

    def test_album_delete_view_permissions(self):
        # Test album delete permissions
        self.client.login(username='artist', password='12345')
        delete_url = reverse('album-delete', args=[self.test_album.id])
        response = self.client.post(delete_url)
        
        # Check for redirect or successful deletion
        self.assertIn(response.status_code, [302, 200])

class APITests(TestCase):
    def setUp(self):
        # Create test user and login
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_profile = MusicManagerUser.objects.create(
            user=self.user,
            display_name='Test User',
            user_type='editor'
        )
        self.client.login(username='testuser', password='12345')
        
        # Create an album
        self.album = Album.objects.create(
            title='API Test Album',
            artist='Test Artist',
            price=9.99,
            format='DD',
            release_date=date.today()
        )

        # Create a song
        self.song = Song.objects.create(
            title='API Test Song',
            length=180
        )

    def test_album_api_list(self):
        # Test to retrieve list of albums
        response = self.client.get(reverse('album-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('API Test Album', str(response.content))

    def test_album_api_detail(self):
        # Retrieving album details
        response = self.client.get(f'/albums/{self.album.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('API Test Album', str(response.content))

class FormTests(TestCase):
    def setUp(self):
        # Song creation test
        self.song = Song.objects.create(
            title='Test Song',
            length=180
        )

    def test_album_form_valid(self):
    # Test to check valid album form submission
        form_data = {
            'title': 'New Album',
            'price': 9.99,
            'format': 'CD',
            'release_date': date.today(),
            'artist': 'Test Artist',  # Add the artist field
            'tracklist': [self.song.id]
        }
        form = AlbumForm(data=form_data)
    
    # If the form is not valid, print out the errors for debugging
        if not form.is_valid():
            print("Form Errors:", form.errors)
        
        self.assertTrue(form.is_valid())

    def test_album_form_invalid(self):
        # Test invalid for album form submission
        form_data = {
            'title': '', 
            'price': 1000,  
            'format': 'XX',  # Invalid format
            'release_date': date.today() + timedelta(days=1800)  # More than 3 years into the future so invalid
        }
        form = AlbumForm(data=form_data)
        self.assertFalse(form.is_valid())


class AdditionalTests(TestCase):
    def setUp(self):
        # Create test users with different profiles
        self.artist_user = User.objects.create_user(username='artist1', password='12345')
        self.artist_profile = MusicManagerUser.objects.create(
            user=self.artist_user,
            display_name='Artist Name',
            user_type='artist'
        )

        # Test dates
        self.song1 = Song.objects.create(
            title='Test Song 1',
            length=180  
        )
        self.song2 = Song.objects.create(
            title='Test Song 2',
            length=240  
        )

    def test_album_multiple_songs(self):
        # Test creating an album with multiple songs
        album = Album.objects.create(
            title='Multi-Song Album',
            artist='Artist Name',
            price=12.99,
            format='VL',
            release_date=date.today()
        )

        # To add multiple songs to the album
        AlbumTracklistItem.objects.create(album=album, song=self.song1, position=1)
        AlbumTracklistItem.objects.create(album=album, song=self.song2, position=2)

        # Check that songs are correctly associated
        self.assertEqual(album.songs.count(), 2)
        self.assertIn(self.song1, album.songs.all())
        self.assertIn(self.song2, album.songs.all())
            

    def test_album_format_choices(self):
        # Test album different format choices
        valid_formats = ['DD', 'CD', 'VL']
        
        for fmt in valid_formats:
            album = Album.objects.create(
                title=f'Test {fmt} Album',
                artist='Artist Name',
                price=9.99,
                format=fmt,
                release_date=date.today()
            )
            self.assertEqual(album.format, fmt)

    def test_tracklist_unique_constraint(self):
        # Tracklist's unique constraint testing
        album = Album.objects.create(
            title='Unique Tracks Album',
            artist='Artist Name',
            price=9.99,
            format='CD',
            release_date=date.today()
        )

        # First addition
        AlbumTracklistItem.objects.create(album=album, song=self.song1, position=1)

        with self.assertRaises(Exception):
            AlbumTracklistItem.objects.create(album=album, song=self.song1, position=2)

    def test_user_type_choices(self):
        # Test user type choices
        valid_user_types = ['artist', 'editor', 'viewer']
        
        for user_type in valid_user_types:
            user = User.objects.create_user(username=f'test_{user_type}', password='12345')
            profile = MusicManagerUser.objects.create(
                user=user,
                display_name=f'Test {user_type}',
                user_type=user_type
            )
            self.assertEqual(profile.user_type, user_type)

    def test_album_slug_generation(self):
        # Test for slug
        album = Album.objects.create(
            title='Slug Test Album',
            artist='Artist Name',
            price=9.99,
            format='DD',
            release_date=date.today()
        )

        # Slug generation
        self.assertEqual(album.slug, 'slug-test-album-dd')

    def test_song_display_in_album(self):
        # To create an album and add songs
        album = Album.objects.create(
            title='Song Display Album',
            artist='Artist Name',
            price=9.99,
            format='CD',
            release_date=date.today()
        )

        # Test to add songs to an album
        AlbumTracklistItem.objects.create(album=album, song=self.song1, position=1)
        AlbumTracklistItem.objects.create(album=album, song=self.song2, position=2)

        # Test to check if the songs are displayed correctly
        self.assertIn(self.song1, album.songs.all())
        self.assertIn(self.song2, album.songs.all())
        self.assertEqual(album.songs.count(), 2)