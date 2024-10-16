from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .query_functions import get_queryset
from .pagination import do_paginate
from .models import User, Post, Category, Comment
from .forms import PostForm, UserEditForm, CommentForm


def index(request):
    """
    Получает список опубликованных постов, разделенных на страницы,
    и отображает шаблон 'blog/index.html'.
    Параметры:
        request (HttpRequest): Текущий HTTP-запрос.
    Возвращает:
        HttpResponse: Отображает шаблон 'blog/index.html'.
    """
    post_list = get_queryset()

    return render(
        request,
        'blog/index.html',
        context={'page_obj': do_paginate(request, post_list)}
    )


def post_detail(request, post_id):
    """
    Отображает конкретный пост.
    Параметры:
        request (HttpRequest): Объект запроса HTTP.
        pk (int): Первичный ключ поста для получения.
    Возвращает:
        HttpResponse: Отображенный HTML-ответ страницы с постом.

    """
    post = get_object_or_404(get_queryset(
        filter=False,
        annotate_and_sort=False
    ), pk=post_id)

    if request.user != post.author:
        # Если юзер не автор поста, то уточняем, что пост доступен.
        post = get_object_or_404(get_queryset(), pk=post_id)

    comments = post.comments.select_related('author').order_by('created_at')
    form = CommentForm()
    return render(
        request,
        'blog/detail.html',
        context={'comments': comments, 'post': post, 'form': form}
    )


def category_posts(request, category_slug):
    """
    Получает отфильтрованный список постов для конкретной категории и
    отображает страницу категории.
    Параметры:
        request (HttpRequest): Текущий объект запроса.
        category_slug (str): Слаг категории, для которой нужно получить посты.
    Возвращает:
        HttpResponse: Отображенный HTML-ответ страницы категории.
    """
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_queryset(manager=category.posts)

    return render(
        request,
        'blog/category.html',
        context={
            'category': category,
            'post_list': post_list,
            'page_obj': do_paginate(request, post_list)}
    )


def profile(request, username):
    """
    Возвращает отображаемую страницу профиля для заданного пользователя.
    Аргументы:
        request (HttpRequest): Объект HTTP-запроса.
        username (str): Имя пользователя.
    Возвращает:
        HttpResponse: Объект HTTP-ответа,
        содержащий отрендеренную страницу профиля.:
        Http404: Если пользователь с заданным именем не существует.
    """
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        posts = get_queryset(manager=profile.posts, filter=False)
    else:
        posts = get_queryset(manager=profile.posts)

    context = {'profile': profile, 'page_obj': do_paginate(request, posts)}
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    """
    Создает новый пост для аутентифицированного пользователя.
    Параметры:
        request (HttpRequest): Объект текущего HTTP-запроса.
    Возвращает:
        HttpResponseRedirect: Если форма действительна,
        перенаправляет на страницу профиля пользователя.
        HttpResponse: Если форма не действительна,
        отрисовывает шаблон 'blog/create.html' с формой.
    """
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('blog:profile', request.user.username)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_profile(request):
    """
    Редактирует профиль пользователя.
    Параметры:
        request: Объект запроса текущего запроса.
    Возвращает:
        Отображенный HTML-ответ страницы профиля пользователя
        или перенаправление на страницу профиля после успешной редакции.
    """
    user = request.user
    form = UserEditForm(instance=user)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=user.username)

    return render(request, 'blog/user.html', {'form': form})


@login_required
def add_comment(request, post_id):
    # Получаем объект или выбрасываем 404 ошибку.
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        # Создаём объект , но не сохраняем его в БД.
        comment = form.save(commit=False)
        # В поле author передаём объект автора
        comment.author = request.user
        comment.post = post
        # Сохраняем объект в БД.
        comment.save()
        # Перенаправляем пользователя назад, на страницу.
    return redirect('blog:post_detail', post_id)


@login_required(login_url='/auth/login/')
def edit_post(request, post_id):
    """
    Редактирование поста.
    Эта функция позволяет автору поста редактировать его.
    Параметры:
    - request (HttpRequest): Текущий HTTP-запрос.
    - post_id (int): ID поста, который нужно отредактировать.
    Возвращает:
    - HttpResponseRedirect: Если пользователь не является автором поста,
      перенаправляет на страницу с детальной информацией о посте.
    - HttpResponse: Если пользователь является автором поста и
    отправляет допустимую форму, перенаправляет на страницу
    с детальной информацией о посте.
    - HttpResponse: Если пользователь является автором поста и
    отправляет недопустимую форму, отображает шаблон 'blog/create.html'
    с формой.
    """
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """
    Удаляет пост.
    Параметры:
        request (HttpRequest): Объект HTTP-запроса.
        post_id (int): ID удаляемого поста.
    Возвращает:
        HttpResponseRedirect: Редирект на главную страницу блога.
        Http404: Если пост с указанным ID не существует.
    """
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        if request.user == post.author:
            post.delete()
        return redirect('blog:index')

    # Если метод GET, отображаем страницу подтверждения
    return render(request, 'blog/create.html', {'post': post})


@login_required
def edit_comment(request, post_id, comment_id):
    """
    Редактирование комментария.
    Позволяет автору комментария редактировать комментарий.
    Параметры:
        request (HttpRequest): Текущий объект запроса.
        post_id (int): ID поста, к которому принадлежит комментарий.
        comment_id (int): ID комментария для редактирования.
    Возвращает:
        HttpResponse: Перенаправление на страницу детализации поста,
        если комментарий успешно отредактирован,
        иначе отображается шаблон с формой комментария.
    """
    comment = get_object_or_404(Comment, pk=comment_id, post__id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_comment(request, post_id, comment_id):
    """
    Удаляет комментарий на основе comment_id
    и перенаправляет на главную страницу.
    Параметры:
        request (HttpRequest): Объект HTTP-запроса.
        post_id (int): ID поста, к которому принадлежит комментарий.
        comment_id (int): ID комментария для удаления.
    Возвращает:
        HttpResponseRedirect: Перенаправляет на 'blog:index'
        после удаления комментария или если его пытается удалить
        не автор поста.
    """
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post__id=post_id,
    )
    context = {'comment': comment}

    if request.method == 'GET':
        return render(request, 'blog/comment.html', context)
    elif request.method == 'POST' and request.user.id == comment.author_id:
        comment.delete()
    return redirect('blog:index')
