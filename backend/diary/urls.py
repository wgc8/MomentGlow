from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'diaries', views.DiaryViewSet, basename='diary')
router.register(r'images', views.DiaryImageViewSet, basename='diary-image')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
] 