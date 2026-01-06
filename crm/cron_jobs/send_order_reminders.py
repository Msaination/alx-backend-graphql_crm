#!/usr/bin/env python3
import sys
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date range (last 7 days)
cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# GraphQL query
query = gql("""
{
  allOrders(orderDate_Gte: "%s") {
    edges {
      node {
        id
        orderDate
        customer {
          email
        }
      }
    }
  }
}
""" % cutoff_date)

try:
    result = client.execute(query)
    orders = result.get("allOrders", {}).get("edges", [])

    for edge in orders:
        order = edge["node"]
        order_id = order["id"]
        customer_email = order["customer"]["email"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info("%s - Reminder: Order %s for customer %s", timestamp, order_id, customer_email)

    print("Order reminders processed!")

except Exception as e:
    logging.error("Error processing reminders: %s", str(e))
    sys.exit(1)
    print("Failed to process order reminders.")