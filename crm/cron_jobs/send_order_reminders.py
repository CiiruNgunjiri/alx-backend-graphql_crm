#!/usr/bin/env python3

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import logging

# Setup logging to file with timestamp
logging.basicConfig(filename='/tmp/order_reminders_log.txt',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

def main():
    # GraphQL client setup
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # GraphQL query to get orders with order_date in last 7 days
    query = gql("""
    query GetRecentOrders($lastWeek: DateTime!) {
        orders(orderDate_Gte: $lastWeek) {
            edges {
                node {
                    id
                    customer {
                        email
                    }
                    orderDate
                }
            }
        }
    }
    """)

    # Calculate datetime for 7 days ago in ISO format
    last_week = datetime.now().isoformat()

    params = {"lastWeek": last_week}

    try:
        # Execute query
        result = client.execute(query, variable_values=params)
        orders = result.get("orders", {}).get("edges", [])

        for order_edge in orders:
            order = order_edge.get("node", {})
            order_id = order.get("id")
            customer_email = order.get("customer", {}).get("email")

            if order_id and customer_email:
                log_msg = f"Order ID: {order_id}, Customer Email: {customer_email}"
                logging.info(log_msg)
        
        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error while fetching orders: {str(e)}")
        print("Failed to process order reminders!")

if __name__ == "__main__":
    main()
