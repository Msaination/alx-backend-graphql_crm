import requests
from datetime import datetime
from celery import shared_task

@shared_task
def generate_crm_report():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"

    query = """
    {
      allCustomers {
        totalCount
      }
      allOrders {
        totalCount
        edges {
          node {
            totalAmount
          }
        }
      }
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            timeout=10
        )
        data = response.json().get("data", {})

        total_customers = data.get("allCustomers", {}).get("totalCount", 0)
        orders_data = data.get("allOrders", {})
        total_orders = orders_data.get("totalCount", 0)

        # Sum revenue
        total_revenue = sum(
            float(order["node"]["totalAmount"])
            for order in orders_data.get("edges", [])
            if order["node"].get("totalAmount") is not None
        )

        report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"

        with open(log_file, "a") as f:
            f.write(report)

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error generating report: {e}\n")
    return "CRM report generated."
