import os
import requests
import logging
import datetime


from requests.auth import HTTPBasicAuth
from collections import Counter

# Retrieve the log level from environment variable or default to INFO
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
numeric_level = getattr(logging, log_level, None)

if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {log_level}')

logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')


USERNAME = os.environ.get('USERNAME')
API_TOKEN = os.environ.get('API_TOKEN')
JIRA_URL = 'https://mluvii.atlassian.net'
CURRENT_DATE = datetime.datetime.now()
DATE_FROM = CURRENT_DATE.strftime("%Y-%m-%d")  # Dnešní datum
DATE_TO = (CURRENT_DATE + datetime.timedelta(days=1)).strftime("%Y-%m-%d") 


def get_hd_issues_total(date_from: str = None, date_to: str = None) -> dict:
    """
    Fetch the total number of HD issues within a specified date range.
    Args:
    date_from: Start date in YYYY-MM-DD format.
    date_to: End date in YYYY-MM-DD format.
    Returns:
    Total number of issues as an integer.
    """
    if date_from is None:
        date_from = DATE_FROM
    if date_to is None:
        date_to = DATE_TO

    logging.debug("Fetching total HD issues count from %s to %s", date_from, date_to)

    query = {
        "jql": f'project = HD AND issuetype = Bug AND created >= "{date_from}" and created <= "{date_to}"',
        "startAt": 0,
        "maxResults": 1000,  # Set to 0 to fetch only total count, not the actual issues
        "fields": ["id", "key"]  # Minimal fields since we only need the count
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f'{JIRA_URL}/rest/api/2/search',
                                 auth=HTTPBasicAuth(USERNAME, API_TOKEN),
                                 headers=headers,
                                 json=query)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error("Request failed: %s", e)
        return 0

    response_data = response.json()
    return response_data.get('total', 0)
    
def count_issues_by_company(date_from: str = None, date_to: str = None) -> dict:
    """
    Count the number of issues reported by each company within a specified date range.

    This function queries a JIRA instance for issues of type 'Bug' in the 'HD' project,
    created between the specified start and end dates. It then tallies these issues based
    on the company reported in a custom field (specified by its ID).

    The function handles pagination in the JIRA API response to ensure all relevant issues
    are counted, regardless of the total number.

    Args:
    date_from (str, optional): The start date for the query in 'YYYY-MM-DD' format. Defaults to DATE_FROM.
    date_to (str, optional): The end date for the query in 'YYYY-MM-DD' format. Defaults to DATE_TO.

    Returns:
    dict: A dictionary where keys are company names and values are the count of issues associated with each company.
          Issues without a company name are counted under the key 'others'.
    """
    if date_from is None:
        date_from = DATE_FROM
    if date_to is None:
        date_to = DATE_TO

    logging.debug("Counting issues by company from %s to %s", date_from, date_to)

    query = {
        "jql": f'project = HD AND issuetype = Bug AND created >= "{date_from}" and created <= "{date_to}"',
        "startAt": 0,
        "maxResults": 10000,  # Adjust based on your needs
        "fields": ["customfield_10002"]  # Replace with the actual custom field ID for the company
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    company_count = Counter()

    while True:
        try:
            response = requests.post(f'{JIRA_URL}/rest/api/2/search',
                                     auth=HTTPBasicAuth(USERNAME, API_TOKEN),
                                     headers=headers,
                                     json=query)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error("Request failed: %s", e)
            break

        data = response.json()
        issues = data.get('issues', [])

        for issue in issues:
            company_data = issue['fields'].get('customfield_10002')  # Adjust the field ID as needed
            if company_data:
                for company_entry in company_data:
                    company_name = company_entry.get('name')  # Extract the company name
                    if company_name:
                        company_count[company_name] += 1
                    else:
                        company_count['others'] += 1

        if not data['startAt'] + data['maxResults'] < data['total']:
            break

        query['startAt'] += data['maxResults']

    return dict(company_count)

def main():
    logging.info("Main function started")
    bug_count = get_hd_issues_total()
    issues_by_company = count_issues_by_company()
    print(issues_by_company)
    print(f"Total bug count: {bug_count}")

if __name__ == "__main__":
    logging.info("Script started")
    main()
    logging.info("Script finished")