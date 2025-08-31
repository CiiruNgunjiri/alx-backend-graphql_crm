import graphene
import re
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from crm.models import Customer, Product, Order
from crm.filters import CustomerFilter, ProductFilter, OrderFilter
from django.db import transaction
from datetime import datetime
from graphql import GraphQLError

# Define GraphQL types:
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        for product in low_stock_products:
            product.stock += 10
            product.save()
        return UpdateLowStockProducts(
            updated_products=low_stock_products,
            message=f"Restocked {low_stock_products.count()} products"
        )

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")

class CustomerInput(graphene.InputObjectType):
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

# Define mutations:
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        name = input.name
        email = input.email
        phone = input.phone

        errors = []

        # Validate email uniqueness
        if Customer.objects.filter(email=email).exists():
            errors.append("Email already exists")

        # Validate phone format (simple example)
        if phone:
            pattern = re.compile(r"^\+?\d[\d\s\-]+\d$")
            if not pattern.match(phone):
                errors.append("Phone number format is invalid")

        if errors:
            return CreateCustomer(success=False, errors=errors)

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, success=True)

class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)  # Output list of created customers
    errors = graphene.List(graphene.String)

    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    def mutate(self, info, customers):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, cust_data in enumerate(customers):
                record_errors = []

                if Customer.objects.filter(email=cust_data.email).exists():
                    record_errors.append(f"Record {idx + 1}: Email '{cust_data.email}' already exists")

                if cust_data.phone:
                    pattern = re.compile(r"^\+?\d[\d\s\-]+\d$")
                    if not pattern.match(cust_data.phone):
                        record_errors.append(f"Record {idx + 1}: Phone number format '{cust_data.phone}' is invalid")

                if record_errors:
                    errors.extend(record_errors)
                    continue

                customer = Customer(
                    name=cust_data.name,
                    email=cust_data.email,
                    phone=cust_data.phone,
                )
                customer.save()
                created_customers.append(customer)

        return BulkCreateCustomers(customers=created_customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)  # Use Decimal scalar here
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=None):
        # Access price which is a decimal.Decimal instance
        errors = []

        if price <= 0:
            errors.append("Price must be positive")
        if stock < 0:
            errors.append("Stock cannot be negative")

        if errors:
            return CreateProduct(success=False, errors=errors)
        
        product = Product(name=name, price=price, stock=stock or 0)
        product.save()
        
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.types.datetime.DateTime(required=False)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        errors = []

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID")

        products = []
        for pid in product_ids:
            try:
                product = Product.objects.get(pk=pid)
                products.append(product)
            except Product.DoesNotExist:
               raise GraphQLError(f"Invalid product ID: {pid}")

        if not products:
            raise GraphQLError("At least one valid product must be selected")

        if errors:
            return CreateOrder(success=False, errors=errors)

        if order_date is None:
            order_date = datetime.now()

        order = Order(customer=customer, order_date=order_date)
        order.save()  # save first to create many-to-many relation

        for product in products:
            order.products.add(product)
        order.total_amount = sum(product.price for product in products)
        order.save()

        return CreateOrder(order=order, success=True)

# Define Mutation Class:
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

# Node types
class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)
        filterset_class = CustomerFilter

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)
        filterset_class = ProductFilter

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)
        filterset_class = OrderFilter

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL")
    
    all_customers = DjangoFilterConnectionField(CustomerNode)
    all_products = DjangoFilterConnectionField(ProductNode)
    all_orders = DjangoFilterConnectionField(OrderNode)

    customer = relay.Node.Field(CustomerNode)
    product = relay.Node.Field(ProductNode)
    order = relay.Node.Field(OrderNode)
    
schema = graphene.Schema(query=Query, mutation=Mutation)