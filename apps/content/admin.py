from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (
    Article,
    BrewMethod,
    Category,
    Ingredient,
    MethodStep,
    MethodTool,
    Recipe,
    RecipeStep,
    Variety,
)

admin.site.site_header = 'Café Legendario'
admin.site.site_title = 'Café Legendario'
admin.site.index_title = 'Administración del contenido'


@admin.action(description='Publicar seleccionados')
def publish(modeladmin, request, queryset):
    updated = 0
    for obj in queryset:
        obj.is_published = True
        try:
            obj.full_clean()
        except ValidationError:
            continue
        obj.save(update_fields=['is_published', 'updated_at'])
        updated += 1
    skipped = queryset.count() - updated
    message = f'{updated} publicado(s).'
    if skipped:
        message += f' {skipped} sin publicar: les falta la fotografía u otro dato obligatorio.'
    modeladmin.message_user(request, message)


@admin.action(description='Despublicar seleccionados')
def unpublish(modeladmin, request, queryset):
    updated = queryset.update(is_published=False)
    modeladmin.message_user(request, f'{updated} despublicado(s).')


class PublishableAdmin(admin.ModelAdmin):
    actions = [publish, unpublish]
    list_filter = ['is_published']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']


class MethodToolInline(admin.TabularInline):
    model = MethodTool
    extra = 1


class MethodStepInline(admin.TabularInline):
    model = MethodStep
    extra = 1


@admin.register(BrewMethod)
class BrewMethodAdmin(PublishableAdmin):
    list_display = ['name', 'ratio', 'time', 'order', 'is_published']
    list_editable = ['order']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']
    inlines = [MethodToolInline, MethodStepInline]


@admin.register(Variety)
class VarietyAdmin(PublishableAdmin):
    list_display = ['name', 'origin', 'is_published']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name', 'origin']


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(PublishableAdmin):
    list_display = ['name', 'category', 'method', 'difficulty', 'prep_minutes', 'featured', 'is_published']
    list_filter = ['is_published', 'featured', 'category', 'method', 'difficulty']
    list_select_related = ['category', 'method']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']
    autocomplete_fields = ['category', 'method']
    inlines = [IngredientInline, RecipeStepInline]


@admin.register(Article)
class ArticleAdmin(PublishableAdmin):
    list_display = ['title', 'topic', 'order', 'is_published']
    list_filter = ['is_published', 'topic']
    list_editable = ['order']
    prepopulated_fields = {'slug': ['title']}
    search_fields = ['title', 'body']
