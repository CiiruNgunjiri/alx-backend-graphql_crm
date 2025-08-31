from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import logging

logging.basicConfig(filename='/tmp/crm_report_log.txt',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql', verify=False)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query {
      totalCustomers: customersCount
      totalOrders: ordersCount
      totalRevenue: ordersAggregate {
        sum {
          totalamount
        }
      }
    }
    """)

    try:
        result = client.execute(query)
        customers = result.get('totalCustomers', 0)
        orders = result.get('totalOrders', 0)
        revenue = result.get('totalRevenue', {}).get('sum', {}).get('totalamount', 0)

        log_msg = f"Report: {customers} customers, {orders} orders, {revenue} revenue"
        logging.info(log_msg)

    except Exception as e:
        logging.error(f"Failed to generate CRM report: {str(e)}")
