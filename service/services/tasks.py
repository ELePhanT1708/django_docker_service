import time

from celery import shared_task
from celery_singleton import Singleton
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import F


@shared_task()
def set_price(subscription_id: int):
    from services.models import Subscription
    with transaction.atomic():
        subscription = Subscription.objects.filter(id=subscription_id).annotate(
            annotated_price=F('service__full_price') * (100 - F('plan__discount_percent')) / 100).first()

        subscription.price = subscription.annotated_price
        subscription.save()
    cache.delete(settings.CACHE_PRICE_NAME)


@shared_task()
def set_comment(subscription_id: int):
    from services.models import Subscription
    with transaction.atomic():
        subscription = Subscription.objects.get(id=subscription_id)

        subscription.comment = 'Comments was created in CElery'
        subscription.save()