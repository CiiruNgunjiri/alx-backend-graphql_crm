#!/bin/bash

# Run Django shell command to delete customers with no orders since one year ago
DELETED_COUNT=$(python3 manage.py shell -c "
from datetime import datetime, timedelta
from crm.models import Customer, Order

one_year_ago = datetime.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__date__lt=one_year_ago).distinct()
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log deleted customer count with timestamp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $DELETED_COUNT\" >> /tmp/customer_cleanup_log.txt
