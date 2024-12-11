from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import AlbumTracklistItemViewSet, AlbumViewSet, SongViewSet
from . import views
from django.conf import settings
from django.contrib.auth.views import LoginView

router = DefaultRouter()
router.register(r'albums', AlbumViewSet)
router.register(r'songs', SongViewSet)
router.register(r'tracklist', AlbumTracklistItemViewSet, )

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),

    # Web application routes
    path('', views.album_list, name='album-list'),
    path('albums/', views.album_list, name='album-list'),
    path('albums/new/', views.album_create, name='album-create'),
    path('albums/<int:id>/', views.album_detail, name='album-detail'),
    path('albums/<int:id>/edit/', views.album_edit, name='album-edit'),
    path('albums/<int:id>/delete/', views.album_delete, name='album-delete'),
    
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
]