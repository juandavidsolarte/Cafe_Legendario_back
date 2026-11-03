from rest_framework import serializers

from .models import Article, BrewMethod, Category, Ingredient, Recipe, Variety


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'name']


class BrewMethodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrewMethod
        fields = ['id', 'slug', 'name', 'summary', 'image', 'ratio', 'grind', 'time']


class BrewMethodDetailSerializer(BrewMethodListSerializer):
    tools = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    steps = serializers.SlugRelatedField(many=True, read_only=True, slug_field='text')

    class Meta(BrewMethodListSerializer.Meta):
        fields = BrewMethodListSerializer.Meta.fields + ['description', 'tools', 'steps', 'tips']


class VarietyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        fields = ['id', 'slug', 'name', 'origin', 'flavor', 'image']


class VarietyDetailSerializer(VarietyListSerializer):
    traits = serializers.ListField(source='trait_list', child=serializers.CharField(), read_only=True)

    class Meta(VarietyListSerializer.Meta):
        fields = VarietyListSerializer.Meta.fields + ['description', 'aroma', 'traits', 'details']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity']


class RecipeListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    method = serializers.SlugRelatedField(read_only=True, slug_field='slug')
    method_name = serializers.CharField(source='method.name', read_only=True)
    difficulty_label = serializers.CharField(source='get_difficulty_display', read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'slug', 'name', 'description', 'image', 'category', 'method', 'method_name',
            'difficulty', 'difficulty_label', 'prep_minutes', 'featured',
        ]


class RecipeDetailSerializer(RecipeListSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    steps = serializers.SlugRelatedField(many=True, read_only=True, slug_field='text')

    class Meta(RecipeListSerializer.Meta):
        fields = RecipeListSerializer.Meta.fields + ['ingredients', 'steps', 'tips']


class ArticleSerializer(serializers.ModelSerializer):
    topic_label = serializers.CharField(source='get_topic_display', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'slug', 'title', 'topic', 'topic_label', 'body', 'image']
