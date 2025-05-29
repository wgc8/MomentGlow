# MomentGlow 日记应用后端

这是一个基于Django REST framework的日记应用后端，提供RESTful API接口。

## 功能特点

- 用户认证和授权
- 日记的CRUD操作
- 支持日记图片上传
- 日记可以设置心情、天气和位置
- 支持公开和私密日记
- 支持按多个条件筛选日记

## 技术栈

- Python 3.8+
- Django 5.0.2
- Django REST framework 3.14.0
- PostgreSQL
- 其他依赖见 requirements.txt

## 安装和运行

1. 克隆项目并进入项目目录
```bash
git clone [repository_url]
cd backend
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 创建.env文件并设置环境变量
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=momentglow_db
DB_USER=postgres
DB_PASSWORD=your-password-here
DB_HOST=localhost
DB_PORT=5432
```

5. 创建数据库
```bash
createdb momentglow_db  # 如果使用PostgreSQL
```

6. 运行数据库迁移
```bash
python manage.py migrate
```

7. 创建超级用户
```bash
python manage.py createsuperuser
```

8. 运行开发服务器
```bash
python manage.py runserver
```

## API端点

- `/api/diaries/` - 日记CRUD操作
- `/api/diaries/public/` - 获取公开日记列表
- `/api/images/` - 日记图片上传和管理
- `/admin/` - 管理界面
- `/api-auth/` - REST framework认证视图

## 开发说明

- 所有API端点都需要认证
- 用户只能访问和修改自己的日记
- 图片上传支持按日期自动分类存储
- 支持通过多个字段进行过滤和搜索

## 许可证

MIT 