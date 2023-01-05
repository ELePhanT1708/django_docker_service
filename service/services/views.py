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
    ).annotate(price=F('service__full_price') * (100 - F('plan__discount_percent'))/100)
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)
        response_data = {'result': response.data, 'total': queryset.aggregate(total=Sum('price')).get('total')}
        response.data = response_data
        return response

