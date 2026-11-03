import django_filters

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    method = django_filters.CharFilter(field_name='method__slug')

    class Meta:
        model = Recipe
        fields = ['category', 'method', 'difficulty', 'featured']
