from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import User


@register(User)
class UserIndex(AlgoliaIndex):
    fields = ('full_name', 'email', 'classe', 'participations_count')
    index_name = 'users'
