from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('methods', views.BrewMethodViewSet)
router.register('varieties', views.VarietyViewSet)
router.register('recipes', views.RecipeViewSet)
router.register('articles', views.ArticleViewSet)

urlpatterns = router.urls
