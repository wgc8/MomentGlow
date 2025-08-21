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
from momentglow.views_base import CustomAPIView
from rest_framework.permissions import AllowAny

# Create your views here.

class TagViewSet(CustomAPIView, viewsets.ModelViewSet):
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

class DiaryViewSet(CustomAPIView, viewsets.ModelViewSet):
    serializer_class = DiarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public', 'mood', 'weather']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']

    # 处理查询
    def get_queryset(self):
        user = self.request.user
        queryset = Diary.objects.filter(models.Q(user=user)).select_related('user').prefetch_related('tags', 'comments')

        # # 处理 user_id 参数
        # user_id = self.request.query_params.get('user_id')
        # if user_id:
        #     queryset = queryset.filter(user=user_id)
        # 处理 mood 参数
        mood = self.request.query_params.get('mood')
        if mood:
            queryset = queryset.filter(mood=mood)
        # 处理 timeRange 参数
        time_range = self.request.query_params.get('timeRange')
        if time_range:
            try:
                start, end = time_range.split(',')
                queryset = queryset.filter(created_at__range=[start, end])
            except ValueError:
                pass
        return queryset
    # 处理创建
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 处理创建
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 处理添加评论
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        diary = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(diary=diary, user=request.user)
        return Response(serializer.data)

    # 处理获取公共日记
    @action(detail=False, methods=['get'], url_path='public', permission_classes=[AllowAny])
    def public(self, request):
        queryset = Diary.objects.filter(is_public=True).select_related('user').prefetch_related('tags', 'comments')
        # 处理 user_id 参数
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        # 处理 mood 参数
        mood = request.query_params.get('mood')
        if mood:
            queryset = queryset.filter(mood=mood)
        # 处理 timeRange 参数
        time_range = request.query_params.get('timeRange')
        if time_range:
            try:
                start, end = time_range.split(',')
                queryset = queryset.filter(created_at__range=[start, end])
            except ValueError:
                pass
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 处理修改日记
    def update(self, request, *args, **kwargs):
        diary = self.get_object()
        serializer = self.get_serializer(diary, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # 处理删除日记
    def destroy(self, request, *args, **kwargs):
        diary = self.get_object()
        self.perform_destroy(diary)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # 处理获取日记详情
    def retrieve(self, request, *args, **kwargs):
        diary = self.get_object()
        serializer = self.get_serializer(diary)
        return Response(serializer.data)

    # 处理获取日记列表
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset();
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class DiaryImageViewSet(CustomAPIView, viewsets.ModelViewSet):
    serializer_class = DiaryImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DiaryImage.objects.filter(diary__user=self.request.user)
    
    def perform_create(self, serializer):
        diary_id = self.request.data.get('diary')
        diary = Diary.objects.get(id=diary_id, user=self.request.user)
        serializer.save(diary=diary)

class CommentViewSet(CustomAPIView, viewsets.ModelViewSet):
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
