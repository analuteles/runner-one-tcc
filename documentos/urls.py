from rest_framework.routers import DefaultRouter

from .views import DocumentoViewSet

router = DefaultRouter()
router.register('', DocumentoViewSet, basename='documento')

urlpatterns = router.urls
