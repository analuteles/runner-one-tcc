from rest_framework.routers import DefaultRouter

from .views import CargaViewSet

router = DefaultRouter()
router.register('', CargaViewSet, basename='carga')

urlpatterns = router.urls
