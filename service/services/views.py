from django.conf import settings
from django.core.cache import cache
from django.db.models import Prefetch, Sum, F
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


# Create your views here.
class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        'service',
        Prefetch('client',
                 queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
    )
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        price_cache = cache.get(settings.CACHE_PRICE_NAME)
        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.CACHE_PRICE_NAME, total_price, 60)

        response_data = {'result': response.data, 'total': total_price}
        response.data = response_data
        return response

