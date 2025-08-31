import logging
from datetime import datetime
import requests
from django.conf import settings

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    # Log message to file, appending (create if doesn't exist)
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message)

    # Optional: Query the GraphQL 'hello' field to verify endpoint
    try:
        url = "http://localhost:8000/graphql"
        query = '{ hello }'
        response = requests.post(url, json={"query": query})
        if response.status_code == 200:
            # Just ensure it contains the 'hello' key
            data = response.json()
            if "data" in data and "hello" in data["data"]:
                # Log success (optional)
                with open("/tmp/crm_heartbeat_log.txt", "a") as f:
                    f.write(f"{timestamp} GraphQL endpoint responded successfully\n")
        else:
            with open("/tmp/crm_heartbeat_log.txt", "a") as f:
                f.write(f"{timestamp} GraphQL endpoint returned status {response.status_code}\n")
    except Exception as e:
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} Failed to reach GraphQL endpoint: {str(e)}\n")

def update_low_stock():
    url = "http://localhost:8000/graphql"
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
        response = requests.post(url, json={'query': mutation})
        response.raise_for_status()
        data = response.json()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        updated_products = data['data']['updateLowStockProducts']['updatedProducts']
        message = data['data']['updateLowStockProducts']['message']

        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} - {message}\n")
            for product in updated_products:
                log_file.write(f"Product: {product['name']}, Stock: {product['stock']}\n")

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} - Error in update_low_stock: {str(e)}\n")