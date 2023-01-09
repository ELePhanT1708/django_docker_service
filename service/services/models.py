from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete

from .reciever import delete_cache_total_sum_price
from .tasks import set_price, set_comment
from clients.models import Client


# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):

        if self.full_price != self.__full_price:
            for sub in self.subscription.all():
                set_price.delay(sub.id)
                set_comment.delay(sub.id)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} : {self.full_price}'


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[
                                                       MaxValueValidator(100)
                                                   ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):

        if self.discount_percent != self.__discount_percent:
            for sub in self.subscription.all():
                set_price.delay(sub.id)
                set_comment.delay(sub.id)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.plan_type} : {self.discount_percent}'


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscription', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscription', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscription', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
    comment = models.CharField(default='', max_length=50)

    def save(self):
        creating = not bool(self.id)
        result = super().save()
        if creating:
            set_price.delay(self.id)
            set_comment.delay(self.id)
        return result

    def __str__(self):
        return f'{self.client} : {self.service} : {self.plan}'


post_delete.connect(delete_cache_total_sum_price, sender=Subscription)
