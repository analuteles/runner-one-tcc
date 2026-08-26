from rest_framework.routers import DefaultRouter

from .views import FeriasViewSet

router = DefaultRouter()
router.register('', FeriasViewSet, basename='ferias')

urlpatterns = router.urls
