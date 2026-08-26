from rest_framework.routers import DefaultRouter

from .views import VeiculoViewSet

router = DefaultRouter()
router.register('', VeiculoViewSet, basename='veiculo')

urlpatterns = router.urls
