from django.db import models
from django.db.models import Count


class PostQuerySet(models.QuerySet):

    def published(self):
        return self.filter(
            is_published=True,
            pub_date__lte=models.functions.Now(),
            category__is_published=True
        )

    def with_relations(self):
        return self.select_related('author', 'location', 'category')

    def with_comment_count(self):
        return self.annotate(comment_count=Count('comments'))
