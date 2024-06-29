# Импортируем функции render и redirect для работы с отображениями и перенаправлениями
from django.shortcuts import render, redirect
# Импортируем модель User и модуль auth для работы с аутентификацией
from django.contrib.auth.models import User, auth
# Импортируем модуль messages для отображения сообщений пользователю
from django.contrib import messages
# Импортируем класс HttpResponse для создания HTTP-ответов
from django.http import HttpResponse
# Импортируем декоратор login_required для ограничения доступа к представлениям
from django.contrib.auth.decorators import login_required
# Импортируем наши модели из текущего приложения
from .models import Profile, Post, LikePost, FollowersCount
# Импортируем функцию chain из itertools для объединения списков
from itertools import chain
# Импортируем модуль random для случайного перемешивания списка
import random


# Декоратор для требуемой авторизации, перенаправляет на страницу входа, если пользователь не авторизован
# @login_required(login_url='signin')
# Определяем представление для главной страницы
def index(request):
    # Получаем объект текущего пользователя
    user_object = User.objects.get(username=request.user.username)
    # Получаем профиль текущего пользователя
    user_profile = Profile.objects.get(user=user_object)

    # Создаём пустые списки для пользователей, за которыми следит текущий пользователь, и их постов
    feed = []

    # Получаем всех пользователей, за которыми следит текущий пользователь
    user_following = FollowersCount.objects.filter(follower=request.user.username)
 
    # Получаем все посты этих пользователей и добавляем их в список feed
    for usernames in user_following:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    # # Объединяем все списки постов в один
    # feed_list = list(chain(*feed))

    # Начинаем обработку предложений пользователей для подписки
    all_users = User.objects.all()
    user_following_all = []

    # Добавляем всех пользователей, за которыми следит текущий пользователь, в список user_following_all
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    # Создаём новый список предложений пользователей, исключая уже следующих и текущего пользователя
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    # Перемешиваем список предложений случайным образом
    random.shuffle(final_suggestions_list)

    # Создаём пустые списки для профилей предложенных пользователей
    username_profile_list = []

    # Получаем профили предложенных пользователей и добавляем их в список username_profile_list
    for user in final_suggestions_list:
        profile_lists = Profile.objects.filter(user=user)
        username_profile_list.append(profile_lists)

    # Объединяем все списки профилей в один
    suggestions_username_profile_list = list(chain(*username_profile_list))

    # Отображаем главную страницу с переданными данными о профиле, постах и предложениях пользователей
    return render(request, 'index.html', {
        'user_profile': user_profile, 
        'posts': feed, 
        'suggestions_username_profile_list': suggestions_username_profile_list[:4]
    })

# Декоратор для требуемой авторизации, перенаправляет на страницу входа, если пользователь не авторизован
@login_required(login_url='signin')
# Определяем представление для загрузки нового поста
def upload(request):
    # Проверяем, что запрос является POST
    if request.method == 'POST':
        # Получаем имя пользователя, изображение и подпись из запроса
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        # Создаём новый объект поста и сохраняем его в базе данных
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        # Перенаправляем на главную страницу
        return redirect('/')
    else:
        # Если запрос не POST, перенаправляем на главную страницу
        return redirect('/')

# Декоратор для требуемой авторизации, перенаправляет на страницу входа, если пользователь не авторизован
@login_required(login_url='signin')
# Определяем представление для поиска пользователей
def search(request):
    # Получаем объект текущего пользователя и его профиль
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # Проверяем, что запрос является POST
    if request.method == 'POST':
        # Получаем имя пользователя из запроса и ищем пользователей с похожими именами
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        # Создаём пустые списки для профилей найденных пользователей
        username_profile_list = []


        # Получаем профили найденных пользователей и добавляем их в список username_profile_list
        for user in username_object:
            profile_lists = Profile.objects.filter(user=user)
            username_profile_list.append(profile_lists)
        
        # Объединяем все списки профилей в один
        username_profile_list = list(chain(*username_profile_list))

    # Отображаем страницу поиска с переданными данными о профиле и найденных пользователях
    return render(request, 'search.html', {
        'user_profile': user_profile, 
        'username_profile_list': username_profile_list
    })

# Декоратор для требуемой авторизации, перенаправляет на страницу входа, если пользователь не авторизован
@login_required(login_url='signin')
# Определяем представление для лайка поста
def like_post(request):
    # Получаем имя пользователя и ID поста из запроса
    username = request.user.username
    post_id = request.GET.get('post_id')

    # Получаем объект поста по его ID
    post = Post.objects.get(id=post_id)

    # Проверяем, поставил ли пользователь уже лайк этому посту
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    # Если лайка нет, создаём новый лайк и увеличиваем количество лайков у поста
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        # Если лайк уже есть, удаляем его и уменьшаем количество лайков у поста
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')

# Декоратор для требуемой авторизации, перенаправляет на страницу входа, если пользователь не авторизован
@login_required(login_url='signin')
# Определяем представление для профиля пользователя
def profile(request, pk):
    # Получаем объект пользователя по имени
    user_object = User.objects.get(username=pk)
    # Получаем профиль пользователя
    user_profile = Profile.objects.get(user=user_object)
    # Получаем все посты пользователя
    user_posts = Post.objects.filter(user=pk)
    # Получаем количество постов пользователя
    user_post_length = len(user_posts)

    # Получаем имя текущего пользователя и имя просматриваемого пользователя
    follower = request.user.username
    user = pk

    # Проверяем, подписан ли текущий пользователь на просматриваемого пользователя
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    # Получаем количество подписчиков и подписок у просматриваемого пользователя
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    # Создаём контекст для передачи данных в шаблон
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    # Отображаем страницу профиля с переданными данными
    return render(request, 'profile.html', context)

# Декоратор для требуемой авторизации, перенаправляет на страницу входа, если пользователь не авторизован
@login_required(login_url='signin')
# Определяем представление для подписки на пользователя
def follow(request):
    # Проверяем, что запрос является POST
    if request.method == 'POST':
        # Получаем имя подписчика и имя пользователя из запроса
        follower = request.POST['follower']
        user = request.POST['user']

        # Проверяем, подписан ли уже текущий пользователь на просматриваемого пользователя
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            # Если подписка уже есть, удаляем её
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            # Если подписки нет, создаём новую
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        # Если запрос не POST, перенаправляем на главную страницу
        return redirect('/')

# Декоратор для требуемой авторизации, перенаправляет на страницу входа, если пользователь не авторизован
@login_required(login_url='signin')
# Определяем представление для настройки профиля пользователя
def settings(request):
    # Получаем профиль текущего пользователя
    user_profile = Profile.objects.get(user=request.user)

    # Проверяем, что запрос является POST
    if request.method == 'POST':
        # Если изображение профиля не изменено, сохраняем текущие данные
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        # Если изображение профиля изменено, сохраняем новые данные
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        # Перенаправляем на страницу настроек
        return redirect('settings')
    # Отображаем страницу настроек с текущими данными профиля
    return render(request, 'setting.html', {'user_profile': user_profile})

# Определяем представление для регистрации пользователя
def signup(request):
    # Проверяем, что запрос является POST
    if request.method == 'POST':
        # Получаем данные из запроса
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Проверяем, совпадают ли введённые пароли
        if password == password2:
            # Проверяем, существует ли уже пользователь с таким email
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            # Проверяем, существует ли уже пользователь с таким именем
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                # Создаём нового пользователя и сохраняем его в базе данных
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Аутентифицируем и логиним нового пользователя
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # Создаём профиль для нового пользователя
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            # Если пароли не совпадают, отображаем сообщение об ошибке
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else:
        # Отображаем страницу регистрации
        return render(request, 'signup.html')

# Определяем представление для входа пользователя
def signin(request):
    # Проверяем, что запрос является POST
    if request.method == 'POST':
        # Получаем данные из запроса
        username = request.POST['username']
        password = request.POST['password']

        # Аутентифицируем пользователя
        user = auth.authenticate(username=username, password=password)

        # Если аутентификация успешна, логиним пользователя и перенаправляем на главную страницу
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            # Если аутентификация неуспешна, отображаем сообщение об ошибке
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        # Отображаем страницу входа
        return render(request, 'signin.html')

# Декоратор для требуемой авторизации, перенаправляет на страницу входа, если пользователь не авторизован
@login_required(login_url='signin')
# Определяем представление для выхода пользователя
def logout(request):
    # Выход пользователя и перенаправление на страницу входа
    auth.logout(request)
    return redirect('signin')
