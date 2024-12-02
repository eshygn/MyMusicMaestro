# Use this file to specify your subapp's routes
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import AlbumViewSet, SongViewSet

router = DefaultRouter()
router.register(r'albums', AlbumViewSet)
router.register(r'songs', SongViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]