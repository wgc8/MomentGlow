from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiaryViewSet, TagViewSet, DiaryImageViewSet, CommentViewSet

app_name = 'diary'

router = DefaultRouter()
router.register(r'', DiaryViewSet, basename='diary')
router.register(r'images', DiaryImageViewSet, basename='diary-image')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
] 