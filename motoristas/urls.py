from rest_framework.routers import DefaultRouter

from .views import MotoristaViewSet

router = DefaultRouter()
router.register('', MotoristaViewSet, basename='motorista')

urlpatterns = router.urls
