#!/usr/bin/env python3
import requests
import logging
from datetime import datetime, timedelta

LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

url = "http://localhost:8000/graphql"

cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

query = """
{
  allOrders(orderDate_Gte: "%s") {
    edges {
      node {
        id
        orderDate
        customer { email }
      }
    }
  }
}
""" % cutoff_date

response = requests.post(url, json={"query": query})
data = response.json()

orders = data.get("data", {}).get("allOrders", {}).get("edges", [])
for edge in orders:
    order = edge["node"]
    order_id = order["id"]
    customer_email = order["customer"]["email"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info("%s - Reminder: Order %s for customer %s", timestamp, order_id, customer_email)

print("Order reminders processed!")
