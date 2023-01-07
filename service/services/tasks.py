import time

from celery import shared_task
from celery_singleton import Singleton
from django.db.models import F


@shared_task()
def set_price(subscription_id: int):
    from services.models import Subscription

    time.sleep(10)
    subscription = Subscription.objects.filter(id=subscription_id).annotate(
        annotated_price=F('service__full_price') * (100 - F('plan__discount_percent'))/100).first()

    subscription.price = subscription.annotated_price
    subscription.save()
