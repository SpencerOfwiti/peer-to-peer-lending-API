import django_filters
from rental.models import Borrowed
import pendulum


class BorrowedFilterSet(django_filters.FilterSet):
    missing = django_filters.BooleanFilter(field_name='returned', lookup_expr='isnull')
    overdue = django_filters.BooleanFilter(method='get_overdue', field_name='returned')

    def get_overdue(self, queryset, field_name, value, ):
        if value:
            return queryset.filter(when__lte=pendulum.now().subtract(months=2))
        return queryset

    class Meta:
        model = Borrowed
        fields = ['what', 'to_who', 'missing', 'overdue']
