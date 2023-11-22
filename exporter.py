import os
import time
import logging
from prometheus_client import start_http_server, Gauge
from jira_api import get_hd_issues_total, count_issues_by_company


# Retrieve the log level from environment variable or default to INFO
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
numeric_level = getattr(logging, log_level, None)

TIME_FOR_NEXT_REQUEST:int = int(os.environ.get('TIME_FOR_NEXT_REQUEST', 60))


if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {log_level}')

logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')


# Metrics
bugs_gauge = Gauge('jira_bugs_count', 'Total number of bugs in JIRA')
bugs_by_company_gauge = Gauge('jira_bugs_by_company', 'Number of bugs in JIRA by company', ['company'])

def update_metrics():
    """Update Prometheus metrics with the latest data from JIRA."""
    try:
        # Get total bug count
        bugs_count = get_hd_issues_total()
        bugs_gauge.set(bugs_count)
        logging.debug(f"Number of bugs {bugs_count}")

        # Get bug count by company
        bugs_by_company = count_issues_by_company()
        logging.debug(f"Number of bugs {bugs_by_company}")
        for company, count in bugs_by_company.items():
            bugs_by_company_gauge.labels(company=company).set(count)

    except Exception as e:
        logging.error(f"Error updating metrics: {e}")

def main():
    # Start the Prometheus HTTP server
    try:
        start_http_server(8000)
        logging.info("Prometheus HTTP server started on port 8000")
        logging.info(f"Time for next request to JIRA set for {TIME_FOR_NEXT_REQUEST}s")
    except Exception as e:
        logging.error(f"Failed to start Prometheus HTTP server: {e}")
        return

    while True:
        update_metrics()
        # Sleep for a defined interval, e.g., 60 seconds
        time.sleep(TIME_FOR_NEXT_REQUEST)

if __name__ == "__main__":
    main()
