import requests
import datetime
import csv
from xml.etree import ElementTree as ET

def fetch_arxiv_papers(subject="cs.CL", last_n_hours=24):
    """
    Fetches the latest papers from arXiv in the given subject area from the last N hours.
    
    Args:
        subject (str): The subject area, e.g., "cs.CL" for Computation and Language.
        last_n_hours (int): The time window in hours for fetching papers.
    
    Returns:
        List of dictionaries containing paper details.
    """
    # Calculate the start time (last 24 hours)
    now = datetime.datetime.utcnow()
    start_time = now - datetime.timedelta(hours=last_n_hours)
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    # arXiv API query URL
    url = f"http://export.arxiv.org/api/query?search_query=cat:{subject}&sortBy=submittedDate&sortOrder=descending"

    # Fetch data
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch data from arXiv API")
        return []

    # Parse XML response
    root = ET.fromstring(response.content)
    ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
    papers = []

    for entry in root.findall('arxiv:entry', ns):
        paper = {
            'title': entry.find('arxiv:title', ns).text.strip(),
            'authors': ', '.join(author.find('arxiv:name', ns).text for author in entry.findall('arxiv:author', ns)),
            'published': entry.find('arxiv:published', ns).text.strip(),
            'link': entry.find('arxiv:id', ns).text.strip()
        }
        # Filter papers based on the published date
        published_date = datetime.datetime.strptime(paper['published'], "%Y-%m-%dT%H:%M:%SZ")
        if published_date >= start_time:
            papers.append(paper)

    return papers

def write_to_csv(papers, filename="arxiv_papers.csv"):
    """
    Writes a list of papers to a CSV file.
    
    Args:
        papers (list): List of dictionaries containing paper details.
        filename (str): The name of the output CSV file.
    """
    if not papers:
        print("No papers to write to CSV.")
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'authors', 'published', 'link'])
        writer.writeheader()
        writer.writerows(papers)

    print(f"Data successfully written to {filename}")

# Main script
if __name__ == "__main__":
    subject = "cs.CL"  # Computation and Language
    last_n_hours = 24  # Fetch papers from the last 24 hours
    papers = fetch_arxiv_papers(subject, last_n_hours)
    write_to_csv(papers, filename="arxiv_computation_language_papers.csv")
