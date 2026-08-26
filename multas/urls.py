from rest_framework.routers import DefaultRouter

from .views import MultaViewSet

router = DefaultRouter()
router.register('', MultaViewSet, basename='multa')

urlpatterns = router.urls
