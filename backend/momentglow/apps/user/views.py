from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from momentglow.views_base import CustomAPIView
from django.utils import timezone
import os
import uuid
from django.conf import settings

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "用户注册成功",
                "username": user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = serializer.validated_data['token']
            refresh = serializer.validated_data['refresh']
            
            # 手动更新用户的last_login字段
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return Response({
                'token': token,
                'refresh': refresh,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(CustomAPIView, generics.RetrieveAPIView):
    """获取指定用户的详细信息"""
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    
    def get_object(self):
        """根据URL中的user_id获取用户"""
        user_id = self.kwargs.get('user_id')
        if user_id:
            return CustomUser.objects.get(id=user_id)
        return self.request.user

class AvatarUploadView(CustomAPIView, APIView):
    permission_classes = (IsAuthenticated,)
    
    def generate_unique_filename(self, original_filename):
        """生成唯一的文件名"""
        # 获取文件扩展名
        file_ext = os.path.splitext(original_filename)[1].lower()
        # 生成UUID作为文件名
        unique_id = str(uuid.uuid4())
        # 组合新的文件名
        new_filename = f"{unique_id}{file_ext}"
        return new_filename
    
    def get_full_url(self, request, path):
        """获取完整的URL"""
        host = request.build_absolute_uri('/').rstrip('/')
        return f"{host}{path}"
    
    def post(self, request):
        """上传用户头像"""
        if 'avatar' not in request.FILES:
            return Response({'error': '请提供头像文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return Response({'error': '只支持JPEG、PNG、GIF格式的图片'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证文件大小（限制为5MB）
        if avatar_file.size > 5 * 1024 * 1024:
            return Response({'error': '头像文件大小不能超过5MB'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = request.user
            
            # 注释掉删除旧头像文件的代码，暂时不需要删除
            # if user.avatar:
            #     if os.path.exists(user.avatar.path):
            #         os.remove(user.avatar.path)
            
            # 生成唯一的文件名
            original_filename = avatar_file.name
            unique_filename = self.generate_unique_filename(original_filename)
            
            # 确保avatars目录存在
            avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            if not os.path.exists(avatars_dir):
                os.makedirs(avatars_dir)
            
            # 构建完整的文件路径
            file_path = os.path.join(avatars_dir, unique_filename)
            
            # 保存文件到本地
            with open(file_path, 'wb+') as destination:
                for chunk in avatar_file.chunks():
                    destination.write(chunk)
            
            # 更新用户头像字段
            user.avatar = f'avatars/{unique_filename}'
            user.save()
            
            # 构建完整的URL
            avatar_url = self.get_full_url(request, f'/media/avatars/{unique_filename}')
            
            return Response({
                'message': '头像上传成功',
                'avatar_url': avatar_url,
                'filename': unique_filename
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': f'头像上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AvatarView(CustomAPIView, APIView):
    permission_classes = (AllowAny,)
    
    def get_full_url(self, request, path):
        """获取当前请求的完整的URL"""
        host = request.build_absolute_uri('/').rstrip('/')
        return f"{host}{path}"
    
    def get(self, request, user_id=None):
        """获取用户头像"""
        try:
            if user_id:
                # 获取指定用户的头像
                user = CustomUser.objects.get(id=user_id)
            else:
                # 获取当前登录用户的头像
                if not request.user.is_authenticated:
                    return Response({'error': '需要登录'}, status=status.HTTP_401_UNAUTHORIZED)
                user = request.user
            
            # 如果用户有头像，返回头像URL
            if user.avatar and hasattr(user.avatar, 'url'):
                avatar_url = self.get_full_url(request, user.avatar.url)
                return Response({
                    'avatar_url': avatar_url,
                    'has_avatar': True
                })
            else:
                # 返回默认头像
                default_avatar_url = self.get_full_url(request, '/media/avatars/default.jpg')
                return Response({
                    'avatar_url': default_avatar_url,
                    'has_avatar': False
                })
                
        except CustomUser.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'获取头像失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 