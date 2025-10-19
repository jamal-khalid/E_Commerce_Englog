from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import serializers


from .models import User, Category, Product, CartItem, Order
from .serializers import (UserRegisterSerializer, UserSerializer, CategorySerializer,
                          ProductSerializer, CartItemSerializer, OrderSerializer)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        cached = cache.get('category_list')
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set('category_list', response.data, timeout=3600)  # cache for 1 hour
        return response

    def perform_update(self, serializer):
        cache.delete('category_list')
        serializer.save()

    def perform_destroy(self, instance):
        cache.delete('category_list')
        instance.delete()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'stock']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']

    def get_queryset(self):
        queryset = super().get_queryset()
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        if price_min is not None:
            queryset = queryset.filter(price__gte=price_min)
        if price_max is not None:
            queryset = queryset.filter(price__lte=price_max)
        return queryset

    def list(self, request, *args, **kwargs):
        cached = cache.get('product_list')
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set('product_list', response.data, timeout=3600)  # cache for 1 hour
        return response

    def perform_update(self, serializer):
        cache.delete('product_list')
        serializer.save()

    def perform_destroy(self, instance):
        cache.delete('product_list')
        instance.delete()

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # If item exists, update quantity instead of creating duplicate
        user = self.request.user
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     return Order.objects.filter(user=self.request.user)
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        # Collect cart items
        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            raise serializers.ValidationError("Cart is empty")

        # Check stock availability
        for item in cart_items:
            if item.product.stock < item.quantity:
                raise serializers.ValidationError(f"Product {item.product.name} is out of stock or insufficient quantity")

        order = serializer.save(user=user)

        # Create order items and decrement stock
        for item in cart_items:
            order.items.create(product=item.product, quantity=item.quantity)
            item.product.stock -= item.quantity
            item.product.save()
        # Clear cart
        cart_items.delete()

        # Clear caches
        cache.delete('product_list')
        cache.delete('category_list')

        return order

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_new = request.data.get('status')
        if status_new not in dict(Order.ORDER_STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = status_new
        order.save()

        # Notify user via channel layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{order.user.id}",
            {
                "type": "order_status_update",
                "content": {"order_id": order.id, "status": order.status}
            }
        )
        return Response({"status": "Order status updated"})

class UserOrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
