from django.shortcuts import render
from django.views.generic import TemplateView


class About(TemplateView):
    """
    Класс предназначен для отображения статичной страницы
    на основе шаблона pages/about.html.
    """

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """
    Класс предназначен для отображения статичной страницы
    на основе шаблона pages/rules.html.
    """

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Возвращает 404 ошибку, если страница не найдена."""
    return render(request, 'pages/404.html', status=404)


def internal_server_error(request):
    """Возвращает 500 ошибку, если ошибка со стороны сервера."""
    return render(request, 'pages/500.html', status=500)


def forbidden(request, exception):
    """Возвращает ошибку 403 - доступ запрещен."""
    return render(request, 'pages/403csrf.html', status=403)
