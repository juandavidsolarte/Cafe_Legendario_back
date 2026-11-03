import shutil
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.content.models import BrewMethod, Category, Recipe, Variety

# GIF de 1x1 px para los campos de imagen.
PIXEL = (
    b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x00\x00\x00\x00\x00,'
    b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
)


TEST_MEDIA = tempfile.mkdtemp()


def tearDownModule():
    shutil.rmtree(TEST_MEDIA, ignore_errors=True)


def make_recipe(name, slug, category, method, **extra):
    data = {
        'description': 'Descripción',
        'prep_minutes': 5,
        'is_published': True,
        'image': SimpleUploadedFile(f'{slug}.gif', PIXEL, content_type='image/gif'),
    }
    data.update(extra)
    return Recipe.objects.create(name=name, slug=slug, category=category, method=method, **data)


@override_settings(MEDIA_ROOT=TEST_MEDIA)
class ContentApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.hot = Category.objects.create(name='Calientes', slug='calientes')
        cls.cold = Category.objects.create(name='Frías', slug='frias')
        cls.espresso = BrewMethod.objects.create(
            name='Espresso', slug='espresso', summary='s', description='d',
            ratio='1 : 2', grind='Fina', time='25 s', is_published=True,
        )
        cls.espresso.steps.create(order=1, text='Muele el café')
        cls.espresso.tools.create(name='Tamper')
        make_recipe('Capuchino', 'capuchino', cls.hot, cls.espresso, difficulty='media', featured=True)
        make_recipe('Latte helado', 'latte-helado', cls.cold, cls.espresso)
        make_recipe('Borrador', 'borrador', cls.hot, cls.espresso, is_published=False)

    def setUp(self):
        self.client = APIClient()

    def names(self, response):
        return sorted(item['name'] for item in response.json()['results'])

    def test_lists_only_published_recipes(self):
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.names(response), ['Capuchino', 'Latte helado'])

    def test_unpublished_recipe_detail_returns_404(self):
        self.assertEqual(self.client.get('/api/recipes/borrador/').status_code, 404)

    def test_recipe_detail_includes_steps(self):
        recipe = Recipe.objects.get(slug='capuchino')
        recipe.steps.create(order=1, text='Prepara el espresso')
        recipe.ingredients.create(name='Leche', quantity='120 ml')
        data = self.client.get('/api/recipes/capuchino/').json()
        self.assertEqual(data['steps'], ['Prepara el espresso'])
        self.assertEqual(data['ingredients'], [{'name': 'Leche', 'quantity': '120 ml'}])
        self.assertEqual(data['difficulty_label'], 'Media')

    def test_filters_and_search(self):
        self.assertEqual(self.names(self.client.get('/api/recipes/?category=frias')), ['Latte helado'])
        self.assertEqual(self.names(self.client.get('/api/recipes/?difficulty=media')), ['Capuchino'])
        self.assertEqual(self.names(self.client.get('/api/recipes/?featured=true')), ['Capuchino'])
        self.assertEqual(self.names(self.client.get('/api/recipes/?search=latte')), ['Latte helado'])
        self.assertEqual(self.names(self.client.get('/api/recipes/?method=v60')), [])

    def test_method_detail(self):
        data = self.client.get('/api/methods/espresso/').json()
        self.assertEqual(data['tools'], ['Tamper'])
        self.assertEqual(data['steps'], ['Muele el café'])

    def test_write_operations_are_not_allowed(self):
        self.assertEqual(self.client.post('/api/recipes/', {'name': 'x'}).status_code, 405)
        self.assertEqual(self.client.delete('/api/recipes/capuchino/').status_code, 405)

    def test_swagger_schema_is_available(self):
        self.assertEqual(self.client.get('/api/schema/').status_code, 200)


class PublishValidationTests(TestCase):
    def test_cannot_publish_without_image(self):
        variety = Variety(
            name='Geisha', slug='geisha', description='d', origin='Etiopía',
            flavor='Floral', aroma='Jazmín', is_published=True,
        )
        with self.assertRaises(ValidationError):
            variety.full_clean()
