from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RegisterView, UserProfileView, CategoryViewSet, ProductViewSet,
                    CartItemViewSet, OrderViewSet, UserOrderHistoryView)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('cart', CartItemViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('orders/history/', UserOrderHistoryView.as_view(), name='order_history'),
    path('', include(router.urls)),
]
