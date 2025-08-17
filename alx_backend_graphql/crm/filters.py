import django_filters
from .models import Customer, Product, Order
from django_filters import OrderingFilter

class CustomerFilter(django_filters.FilterSet):
    # Filters with field_name matching model fields and lookups for filtering
    name_icontains = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    email_icontains = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    created_at_gte = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_at_lte = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")
    phone_pattern = django_filters.CharFilter(method="filter_by_phone_pattern")
    order_by = OrderingFilter(
        fields=(('created_at', 'created_at'), ('name', 'name')))
    
    def filter_by_phone_pattern(self, queryset, name, value):
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = ['name_icontains', 'email_icontains', 'created_at_gte', 'created_at_lte', 'phone_pattern']
    
class ProductFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    price_gte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_lte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    stock_gte = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock_lte = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ['name_icontains', 'price_gte', 'price_lte', 'stock_gte', 'stock_lte']

class OrderFilter(django_filters.FilterSet):
    # For related fields, use Django ORM-style lookups with double underscores
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr="icontains")
    product_name = django_filters.CharFilter(field_name="products__name", lookup_expr="icontains")
    total_amount_gte = django_filters.NumberFilter(field_name="total_amount", lookup_expr="gte")

    class Meta:
        model = Order
        fields = ['customer_name', 'product_name', 'total_amount_gte']
