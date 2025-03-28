from django.db import models
from django.utils.timezone import now


class PostQuerySet(models.QuerySet):
    """QuerySet для модели Post."""

    def published(self):
        """Фильтрует только опубликованные посты."""
        return self.filter(
            pub_date__lte=now(),
            is_published=True,
            category__is_published=True
        )

    def with_relations(self):
        """Добавляет select_related."""
        return self.select_related('category', 'location', 'author')
