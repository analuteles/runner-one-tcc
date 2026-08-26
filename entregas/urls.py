from rest_framework.routers import DefaultRouter

from .views import EntregaViewSet

router = DefaultRouter()
router.register('', EntregaViewSet, basename='entrega')

urlpatterns = router.urls
