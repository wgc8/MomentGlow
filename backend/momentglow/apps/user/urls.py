from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, ProfileView, LoginView, AvatarUploadView, AvatarView

app_name = 'user'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profiles/<int:user_id>/', ProfileView.as_view(), name='profile'),
    path('avatar/upload/', AvatarUploadView.as_view(), name='avatar_upload'),
    path('avatar/', AvatarView.as_view(), name='avatar'),
    path('avatar/<int:user_id>/', AvatarView.as_view(), name='avatar_by_id'),
] 