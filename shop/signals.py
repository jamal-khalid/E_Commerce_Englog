from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Order  


@receiver(post_save, sender=Order)
def notify_user_order_update(sender, instance, created, **kwargs):
    user_id = instance.user.id
    channel_layer = get_channel_layer()
    group_name = f"user_{user_id}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "order_status_update",
            "content": {
                "order_id": instance.id,
                "status": instance.status,
                "message": "Your order has been updated."
            },
        },
    )
