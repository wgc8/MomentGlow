from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Diary, DiaryImage, Tag, Comment
from .serializers import (
    DiarySerializer, DiaryImageSerializer, 
    TagSerializer, CommentSerializer
)

# Create your views here.

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True)
    def diaries(self, request, pk=None):
        """获取特定标签下的所有日记"""
        tag = self.get_object()
        diaries = tag.diaries.filter(is_public=True)
        serializer = DiarySerializer(diaries, many=True)
        return Response(serializer.data)

class DiaryFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()
    mood = filters.CharFilter(lookup_expr='icontains')
    weather = filters.CharFilter(lookup_expr='icontains')
    location = filters.CharFilter(lookup_expr='icontains')
    tags = filters.ModelMultipleChoiceFilter(
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
    filterset_class = DiaryFilter
    
    def get_queryset(self):
        """根据用户权限返回日记列表"""
        user = self.request.user
        # 如果是获取公开日记列表
        if self.action == 'public':
            return Diary.objects.filter(is_public=True)
        # 否则只返回用户自己的日记
        return Diary.objects.filter(author=user)
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        """获取公开日记列表"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class DiaryImageViewSet(viewsets.ModelViewSet):
    serializer_class = DiaryImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DiaryImage.objects.filter(diary__author=self.request.user)
    
    def perform_create(self, serializer):
        diary_id = self.request.data.get('diary')
        diary = Diary.objects.get(id=diary_id, author=self.request.user)
        serializer.save(diary=diary)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Comment.objects.filter(parent=None)  # 只返回父评论
    
    def perform_create(self, serializer):
        diary_id = self.request.data.get('diary')
        diary = Diary.objects.get(id=diary_id)
        if not diary.is_public and diary.author != self.request.user:
            raise permissions.PermissionDenied("不能评论非公开的日记")
        serializer.save(diary=diary)
