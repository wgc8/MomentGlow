from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    """标签模型"""
    name = models.CharField('标签名', max_length=50, unique=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Diary(models.Model):
    """日记模型"""
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diaries', verbose_name='作者')
    mood = models.CharField('心情', max_length=50, blank=True)
    weather = models.CharField('天气', max_length=50, blank=True)
    location = models.CharField('位置', max_length=200, blank=True)
    is_public = models.BooleanField('是否公开', default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name='diaries', verbose_name='标签')
    
    class Meta:
        verbose_name = '日记'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class DiaryImage(models.Model):
    """日记图片模型"""
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name='images', verbose_name='日记')
    image = models.ImageField('图片', upload_to='diary_images/%Y/%m/%d/')
    created_at = models.DateTimeField('上传时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '日记图片'
        verbose_name_plural = verbose_name
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.diary.title}的图片 - {self.id}"

class Comment(models.Model):
    """评论模型"""
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name='comments', verbose_name='日记')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='评论者')
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('评论时间', auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='replies', verbose_name='父评论')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author.username}对{self.diary.title}的评论"
