from django.contrib import admin
from .models import Diary, DiaryImage, Tag, Comment

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    date_hierarchy = 'created_at'

@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at', 'mood', 'weather', 'is_public']
    list_filter = ['is_public', 'created_at', 'mood', 'weather']
    search_fields = ['title', 'content', 'author__username']
    date_hierarchy = 'created_at'
    filter_horizontal = ['tags']

@admin.register(DiaryImage)
class DiaryImageAdmin(admin.ModelAdmin):
    list_display = ['diary', 'image', 'created_at']
    list_filter = ['created_at']
    search_fields = ['diary__title']
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['diary', 'author', 'content', 'created_at', 'parent']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'diary__title']
    date_hierarchy = 'created_at'
