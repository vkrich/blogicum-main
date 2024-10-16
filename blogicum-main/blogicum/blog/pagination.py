from django.core.paginator import Paginator
from django.conf import settings


def do_paginate(request, post_list, nums_of_post=settings.NUMS_OF_POST):
    """
    Функция возвращает объект, который делит на страницы посты.
    Параметры:
        request - объект запроса
        post_list - список постов
        nums_of_post - количество постов на страницу
    """
    paginator = Paginator(post_list, nums_of_post)
    page_number = request.GET.get('page')

    return paginator.get_page(page_number)
