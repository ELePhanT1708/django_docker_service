from rest_framework import serializers

from services.models import Subscription, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('__all__')


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    client_name = serializers.CharField(source='client.company_name')
    email = serializers.CharField(source='client.user.email')
    price_from_python = serializers.SerializerMethodField()
    price_from_db = serializers.SerializerMethodField()

    def get_price_from_python(self, instance):
        return instance.service.full_price * (100 - instance.plan.discount_percent)/100

    def get_price_from_db(self, instance):
        return instance.price

    class Meta:
        model = Subscription
        fields = ('id', 'plan_id', 'client_name', 'email', 'plan', 'price_from_python', 'price_from_db')
