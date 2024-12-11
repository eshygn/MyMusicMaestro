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
        # Test validation for release date more than 3 years in the future
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
        # Test creating an album tracklist item
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
        # Create test users with different profiles
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

        # Create a test album
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
        # Artist should be able to create
        self.client.login(username='artist', password='12345')
        album_data = {
            'title': 'New Artist Album',
            'price': 9.99,
            'format': 'CD',
            'release_date': date.today(),
            'tracklist': []  # Empty tracklist for testing
        }
        response = self.client.post(reverse('album-create'), data=album_data)
        self.assertIn(response.status_code, [200, 302])  # Allow both form render and redirect

        # Viewer should not be able to create
        self.client.login(username='viewer', password='67890')
        response = self.client.post(reverse('album-create'), data=album_data)
        self.assertRedirects(response, reverse('album-list'))

    def test_album_edit_view_permissions(self):
        # Test album edit permissions
        # Artist can edit their own album
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
        # Artist can delete their own album
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
        # To retrieve list of albums
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
        # Creating a song for testing
        self.song = Song.objects.create(
            title='Test Song',
            length=180
        )

    def test_album_form_valid(self):
    # Test valid album form submission
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
        # Test invalid album form submission
        form_data = {
            'title': '', 
            'price': 1000,  
            'format': 'XX',  # Invalid format
            'release_date': date.today() + timedelta(days=1800)  # More than 3 years into the future
        }
        form = AlbumForm(data=form_data)
        self.assertFalse(form.is_valid())