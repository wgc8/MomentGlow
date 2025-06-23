from rest_framework import serializers
from .models import Diary, DiaryImage, Tag, Comment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'user_username']
        read_only_fields = ['user']

class DiaryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryImage
        fields = ['id', 'image', 'created_at']

class DiarySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    images = DiaryImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Diary
        fields = [
            'id', 'title', 'content', 'created_at', 'updated_at',
            'mood', 'weather', 'location', 'is_public',
            'user', 'tags', 'comments', 'user_username','images'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        diary = Diary.objects.create(**validated_data)
        
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            diary.tags.add(tag)
        
        return diary

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        diary = super().update(instance, validated_data)
        
        if tags_data:
            # 清除现有标签
            diary.tags.clear()
            # 添加新标签
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(**tag_data)
                diary.tags.add(tag)
        
        return diary 