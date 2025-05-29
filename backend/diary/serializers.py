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
        fields = ['id', 'name', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'author', 'parent', 'replies']
        read_only_fields = ['created_at']

    def get_replies(self, obj):
        if obj.parent is None:  # 只有父评论才获取回复
            replies = obj.replies.all()
            return CommentSerializer(replies, many=True).data
        return []

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class DiaryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryImage
        fields = ['id', 'image', 'created_at']

class DiarySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    images = DiaryImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Diary
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 
                 'author', 'mood', 'weather', 'location', 'is_public', 
                 'images', 'tags', 'comments']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        validated_data['author'] = self.context['request'].user
        diary = super().create(validated_data)
        
        # 处理标签
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