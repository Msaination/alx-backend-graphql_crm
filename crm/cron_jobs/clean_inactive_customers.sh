#!/bin/bash

# Navigate to project root (adjust path if needed)
cd /Users/msiko/Sites/ProDevBE/alx-backend-graphql_crm || exit

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell <<EOF
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True, created_at__lt=cutoff).distinct()
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log result with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
