# Импортируем модуль models из Django для создания моделей
from django.db import models
# Импортируем функцию get_user_model из Django для получения пользовательской модели
from django.contrib.auth import get_user_model
# Импортируем модуль uuid для создания уникальных идентификаторов
import uuid
# Импортируем модуль datetime для работы с датой и временем
from datetime import datetime

# Получаем пользовательскую модель, определённую в настройках Django
User = get_user_model()

# Создаём модель Profile, представляющую профиль пользователя
class Profile(models.Model):
    # Связываем профиль с пользователем через внешний ключ
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Поле для хранения биографии пользователя, может быть пустым
    bio = models.TextField(blank=True)
    # Поле для хранения изображения профиля, загружаемого в папку 'profile_images'
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    # Поле для хранения местоположения пользователя, может быть пустым
    location = models.CharField(max_length=100, blank=True)

    # Метод для представления модели в виде строки
    def __str__(self):
        return self.user.username

# Создаём модель Post, представляющую пост пользователя
class Post(models.Model):
    # Поле для хранения уникального идентификатора поста
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # Поле для хранения имени пользователя
    user = models.CharField(max_length=100)
    # Поле для хранения изображения поста, загружаемого в папку 'post_images'
    image = models.ImageField(upload_to='post_images')
    # Поле для хранения подписи к посту
    caption = models.TextField()
    # Поле для хранения даты и времени создания поста
    created_at = models.DateTimeField(default=datetime.now)
    # Поле для хранения количества лайков у поста
    no_of_likes = models.IntegerField(default=0)

    # Метод для представления модели в виде строки
    def __str__(self):
        return self.user

# Создаём модель LikePost, представляющую лайк к посту
class LikePost(models.Model):
    # Поле для хранения идентификатора поста
    post_id = models.CharField(max_length=500)
    # Поле для хранения имени пользователя, который поставил лайк
    username = models.CharField(max_length=100)

    # Метод для представления модели в виде строки
    def __str__(self):
        return self.username

# Создаём модель FollowersCount, представляющую количество подписчиков пользователя
class FollowersCount(models.Model):
    # Поле для хранения имени подписчика
    follower = models.CharField(max_length=100)
    # Поле для хранения имени пользователя, на которого подписаны
    user = models.CharField(max_length=100)

    # Метод для представления модели в виде строки
    def __str__(self):
        return self.user
