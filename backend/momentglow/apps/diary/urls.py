from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiaryViewSet, TagViewSet

app_name = 'diary'

router = DefaultRouter()
router.register(r'diaries', DiaryViewSet, basename='diary')
router.register(r'images', views.DiaryImageViewSet, basename='diary-image')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
] 