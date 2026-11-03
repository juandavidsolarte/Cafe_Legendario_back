"""Endpoints públicos de solo lectura. Solo exponen contenido publicado."""

from rest_framework import viewsets

from .filters import RecipeFilter
from .models import Article, BrewMethod, Category, Recipe, Variety
from .serializers import (
    ArticleSerializer,
    BrewMethodDetailSerializer,
    BrewMethodListSerializer,
    CategorySerializer,
    RecipeDetailSerializer,
    RecipeListSerializer,
    VarietyDetailSerializer,
    VarietyListSerializer,
)


class ListDetailMixin:
    """Usa un serializer ligero para listados y uno completo para el detalle."""

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class:
            return self.detail_serializer_class
        return super().get_serializer_class()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = None


class BrewMethodViewSet(ListDetailMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BrewMethod.objects.published().prefetch_related('tools', 'steps')
    serializer_class = BrewMethodListSerializer
    detail_serializer_class = BrewMethodDetailSerializer
    lookup_field = 'slug'
    pagination_class = None


class VarietyViewSet(ListDetailMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Variety.objects.published()
    serializer_class = VarietyListSerializer
    detail_serializer_class = VarietyDetailSerializer
    lookup_field = 'slug'
    search_fields = ['name', 'origin']


class RecipeViewSet(ListDetailMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        Recipe.objects.published()
        .select_related('category', 'method')
        .prefetch_related('ingredients', 'steps')
    )
    serializer_class = RecipeListSerializer
    detail_serializer_class = RecipeDetailSerializer
    lookup_field = 'slug'
    filterset_class = RecipeFilter
    search_fields = ['name']
    ordering_fields = ['name', 'prep_minutes']


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.published()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'
    filterset_fields = ['topic']
    pagination_class = None
