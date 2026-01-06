import requests
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Update low stock products and log the updates
def update_low_stock():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"

    mutation = """
    mutation {
      updateLowStockProducts {
        updatedProducts {
          id
          name
          stock
        }
        message
      }
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": mutation},
            timeout=10
        )
        data = response.json()
        updates = data.get("data", {}).get("updateLowStockProducts", {})

        with open(log_file, "a") as f:
            f.write(f"{timestamp} - {updates.get('message')}\n")
            for product in updates.get("updatedProducts", []):
                f.write(f"{timestamp} - {product['name']} restocked to {product['stock']}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error: {e}\n")

# Log CRM heartbeat
def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    # Append to heartbeat log
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message)

    # Optional: query GraphQL hello field to verify endpoint
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        data = response.json()
        hello_value = data.get("data", {}).get("hello", "")
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL hello response: {hello_value}\n")
    except Exception as e:
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {e}\n")
