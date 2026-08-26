from rest_framework.routers import DefaultRouter

from .views import PedidoViewSet

router = DefaultRouter()
router.register('', PedidoViewSet, basename='pedido')

urlpatterns = router.urls
