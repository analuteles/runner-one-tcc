from rest_framework.routers import DefaultRouter

from .views import OcorrenciaViewSet

router = DefaultRouter()
router.register('', OcorrenciaViewSet, basename='ocorrencia')

urlpatterns = router.urls
