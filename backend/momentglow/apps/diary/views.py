from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import Diary, DiaryImage, Tag, Comment
from .serializers import (
    DiarySerializer, DiaryImageSerializer, 
    TagSerializer, CommentSerializer
)
from django.db import models

# Create your views here.

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    @action(detail=True)
    def diaries(self, request, pk=None):
        """获取特定标签下的所有日记"""
        tag = self.get_object()
        diaries = tag.diaries.filter(is_public=True)
        serializer = DiarySerializer(diaries, many=True)
        return Response(serializer.data)

class DiaryFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()
    mood = django_filters.CharFilter(lookup_expr='icontains')
    weather = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__name',
        to_field_name='name'
    )

    class Meta:
        model = Diary
        fields = ['created_at', 'mood', 'weather', 'location', 'is_public', 'tags']

class DiaryViewSet(viewsets.ModelViewSet):
    serializer_class = DiarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public', 'mood', 'weather']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        user = self.request.user
        # 返回用户自己的日记和其他用户公开的日记
        return Diary.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        ).select_related('user').prefetch_related('tags', 'comments')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        diary = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(diary=diary, user=request.user)
        return Response(serializer.data)
        return Response(serializer.errors, status=400)

class DiaryImageViewSet(viewsets.ModelViewSet):
    serializer_class = DiaryImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DiaryImage.objects.filter(diary__user=self.request.user)
    
    def perform_create(self, serializer):
        diary_id = self.request.data.get('diary')
        diary = Diary.objects.get(id=diary_id, user=self.request.user)
        serializer.save(diary=diary)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Comment.objects.filter(parent=None)  # 只返回父评论
    
    def perform_create(self, serializer):
        diary_id = self.request.data.get('diary')
        diary = Diary.objects.get(id=diary_id)
        if not diary.is_public and diary.user != self.request.user:
            raise permissions.PermissionDenied("不能评论非公开的日记")
        serializer.save(diary=diary)
