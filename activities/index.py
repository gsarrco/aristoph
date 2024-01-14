from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import Activity


@register(Activity)
class ActivityIndex(AlgoliaIndex):
    fields = ('name', 'allow_new_reservations', 'future_meetings_count')
    index_name = 'activities'
    should_index = 'is_visible'
