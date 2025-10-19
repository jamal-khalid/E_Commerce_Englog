from django.contrib import admin
from .models import User , Category , Product, CartItem , Order , OrderItem
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_user_order_update(user_id, content):
    channel_layer = get_channel_layer()
    group_name = f"user_{user_id}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "order_status_update",
            "content": content,
        },
    )

class OrderAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        notify_user_order_update(obj.user.id, {
            "order_id": obj.id,
            "status": obj.status,
            "message": "Your order has been updated."
        })

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)