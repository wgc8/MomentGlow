from django.apps import AppConfig

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'momentglow.apps.user'
    verbose_name = '用户管理' 