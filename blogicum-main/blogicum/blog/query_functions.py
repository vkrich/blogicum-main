from django.db.models import Count
from django.utils import timezone
from blog.models import Post


def get_queryset(
    manager=Post.objects,
    filter=True,
    annotate_and_sort=True
):
    """
    Возвращает Queryset модели Post с
    заданными JOIN'ами.
    Параметры:
        manager (Queryset): Queryset модели Post.
        filter: Значение True, если нужно отфильтровать посты
        annotate_and_sort: Значение True, если нужно отсортировать посты
                           и добавить метод annotate.
    """
    queryset = manager.select_related('author', 'location', 'category')

    if filter:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    if annotate_and_sort:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    return queryset
