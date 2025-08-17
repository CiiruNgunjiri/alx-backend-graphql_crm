import os
import django
import random
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed():
    print("Seeding data...")

    # Clear existing data
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()

    # Create customers
    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Charlie Brown", "email": "charlie@example.com", "phone": None},
    ]
    customers = []
    for cdata in customers_data:
        customer = Customer.objects.create(**cdata)
        customers.append(customer)

    # Create products
    products_data = [
        {"name": "Laptop", "price": 999.99, "stock": 10},
        {"name": "Smartphone", "price": 599.99, "stock": 25},
        {"name": "Headphones", "price": 199.99, "stock": 50},
    ]
    products = []
    for pdata in products_data:
        product = Product.objects.create(**pdata)
        products.append(product)

    # Create orders (randomly associating customers and products)
    for i in range(5):
        customer = random.choice(customers)
        selected_products = random.sample(products, k=random.randint(1, len(products)))
        order = Order.objects.create(customer=customer, order_date=datetime.now())
        order.products.set(selected_products)
        order.total_amount = sum(p.price for p in selected_products)
        order.save()

    print("Seeding complete")

if __name__ == "__main__":
    seed()
