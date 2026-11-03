from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class PublishableModel(models.Model):
    """Base para todo contenido que el administrador publica o despublica."""

    is_published = models.BooleanField('publicado', default=False, db_index=True)
    created_at = models.DateTimeField('creado', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado', auto_now=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.is_published and not getattr(self, 'image', True):
            raise ValidationError({'image': 'Agrega una fotografía antes de publicar.'})


class Category(models.Model):
    name = models.CharField('nombre', max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class BrewMethod(PublishableModel):
    name = models.CharField('nombre', max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    summary = models.CharField('resumen', max_length=200)
    description = models.TextField('descripción')
    image = models.ImageField('fotografía', upload_to='methods/', blank=True)
    ratio = models.CharField('proporción café : agua', max_length=20, help_text='Ejemplo: 1 : 15')
    grind = models.CharField('molienda', max_length=40)
    time = models.CharField('tiempo estimado', max_length=30, help_text='Ejemplo: 4 min')
    tips = models.TextField('consejos', blank=True)
    order = models.PositiveSmallIntegerField('orden', default=0)

    class Meta:
        verbose_name = 'método de preparación'
        verbose_name_plural = 'métodos de preparación'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MethodTool(models.Model):
    method = models.ForeignKey(BrewMethod, on_delete=models.CASCADE, related_name='tools')
    name = models.CharField('herramienta', max_length=80)
    order = models.PositiveSmallIntegerField('orden', default=0)

    class Meta:
        verbose_name = 'herramienta'
        verbose_name_plural = 'herramientas'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class MethodStep(models.Model):
    method = models.ForeignKey(BrewMethod, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveSmallIntegerField('paso')
    text = models.TextField('instrucción')

    class Meta:
        verbose_name = 'paso'
        verbose_name_plural = 'pasos'
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['method', 'order'], name='unique_method_step_order'),
        ]

    def __str__(self):
        return f'{self.order}. {self.text[:40]}'


class Variety(PublishableModel):
    name = models.CharField('nombre', max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.TextField('descripción')
    origin = models.CharField('origen', max_length=150)
    flavor = models.CharField('perfil de sabor', max_length=150)
    aroma = models.CharField('aroma', max_length=150)
    traits = models.TextField('características', blank=True, help_text='Una característica por línea.')
    details = models.TextField('información relevante', blank=True)
    image = models.ImageField('fotografía', upload_to='varieties/', blank=True)

    class Meta:
        verbose_name = 'variedad'
        verbose_name_plural = 'variedades'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def trait_list(self):
        return [line.strip() for line in self.traits.splitlines() if line.strip()]


class Recipe(PublishableModel):
    class Difficulty(models.TextChoices):
        EASY = 'facil', 'Fácil'
        MEDIUM = 'media', 'Media'
        ADVANCED = 'avanzada', 'Avanzada'

    name = models.CharField('nombre', max_length=120)
    slug = models.SlugField(max_length=130, unique=True)
    description = models.TextField('descripción')
    image = models.ImageField('fotografía principal', upload_to='recipes/', blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='recipes', verbose_name='categoría'
    )
    method = models.ForeignKey(
        BrewMethod, on_delete=models.PROTECT, related_name='recipes', verbose_name='método'
    )
    difficulty = models.CharField(
        'dificultad', max_length=10, choices=Difficulty.choices, default=Difficulty.EASY
    )
    prep_minutes = models.PositiveIntegerField(
        'tiempo de preparación (min)', validators=[MinValueValidator(1), MaxValueValidator(2880)]
    )
    tips = models.TextField('consejos y recomendaciones', blank=True)
    featured = models.BooleanField('destacada', default=False)

    class Meta:
        verbose_name = 'receta'
        verbose_name_plural = 'recetas'
        ordering = ['-featured', 'name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField('ingrediente', max_length=100)
    quantity = models.CharField('cantidad', max_length=60)
    order = models.PositiveSmallIntegerField('orden', default=0)

    class Meta:
        verbose_name = 'ingrediente'
        verbose_name_plural = 'ingredientes'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.name} ({self.quantity})'


class RecipeStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveSmallIntegerField('paso')
    text = models.TextField('instrucción')

    class Meta:
        verbose_name = 'paso'
        verbose_name_plural = 'pasos'
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'order'], name='unique_recipe_step_order'),
        ]

    def __str__(self):
        return f'{self.order}. {self.text[:40]}'


class Article(PublishableModel):
    class Topic(models.TextChoices):
        HISTORY = 'historia', 'Historia'
        ORIGIN = 'origen', 'Origen'
        REGIONS = 'regiones', 'Regiones productoras'
        PROCESSING = 'procesamiento', 'Producción y procesamiento'
        CURIOSITIES = 'curiosidades', 'Curiosidades'
        WORLD = 'cultura', 'Cultura cafetera mundial'
        COLOMBIA = 'colombia', 'Café en Colombia'

    title = models.CharField('título', max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    topic = models.CharField('tema', max_length=20, choices=Topic.choices)
    body = models.TextField('contenido')
    image = models.ImageField('fotografía', upload_to='articles/', blank=True)
    order = models.PositiveSmallIntegerField('orden', default=0)

    class Meta:
        verbose_name = 'artículo educativo'
        verbose_name_plural = 'artículos educativos'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
