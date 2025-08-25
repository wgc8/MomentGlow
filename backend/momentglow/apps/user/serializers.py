from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'password2', 'email', 'avatar')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次输入的密码不匹配"})
        return attrs

    def create(self, validated_data):
        avatar = validated_data.pop('avatar', None)
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        if avatar:
            user.avatar = avatar
            user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'avatar_url', 'bio', 'date_joined')
        read_only_fields = ('id', 'date_joined')
    
    def get_avatar_url(self, obj):
        """返回用户头像URL，如果用户没有设置头像则返回默认头像"""
        request = self.context.get('request')
        if request is not None:
            # 获取完整的host信息
            host = request.build_absolute_uri('/').rstrip('/')
            
            if obj.avatar and hasattr(obj.avatar, 'url'):
                # 返回完整的URL
                return f"{host}{obj.avatar.url}"
            else:
                # 返回默认头像的完整URL
                return f"{host}/media/default.jpg"
        else:
            # 如果没有request上下文，返回相对路径
            if obj.avatar and hasattr(obj.avatar, 'url'):
                return obj.avatar.url
            else:
                return '/media/default.jpg'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('用户账号已被禁用')
                
                # 生成JWT令牌
                refresh = RefreshToken.for_user(user)
                
                attrs['user'] = user
                attrs['token'] = str(refresh.access_token)
                attrs['refresh'] = str(refresh)
                return attrs
            else:
                raise serializers.ValidationError('用户名或密码错误')
        else:
            raise serializers.ValidationError('请提供用户名和密码') 