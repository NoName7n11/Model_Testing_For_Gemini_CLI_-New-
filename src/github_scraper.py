import os
import requests
import json
from dotenv import load_dotenv

# Load GitHub Token from .env file
load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

HEADERS = {
    'Authorization': f'bearer {GITHUB_TOKEN}',
    'Content-Type': 'application/json',
}

# Example GraphQL query to fetch merged pull requests that also close issues
GRAPHQL_QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(states: MERGED, first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        number
        title
        url
        mergedAt
        baseRefOid # Commit before merge
        headRefOid # Commit of the PR branch
        changedFiles
        # We want complex PRs touching multiple files (heuristics)
        closingIssuesReferences(first: 5) {
          nodes {
            number
            title
            body
          }
        }
      }
    }
  }
}
"""

def fetch_complex_prs(owner: str, name: str, min_files: int = 4):
    """
    Fetch merged PRs from a repository that touch a minimum number of files
    and are linked to actual issues (indicating a bug fix or feature request).
    """
    if not GITHUB_TOKEN:
        print("Warning: GITHUB_TOKEN not found in environment.")
        return []

    print(f"Fetching data for {owner}/{name}...")
    url = 'https://api.github.com/graphql'
    variables = {
        "owner": owner,
        "name": name,
        "cursor": None
    }

    candidates = []
    # Simplified loop for demonstration - fetching first page
    response = requests.post(url, json={'query': GRAPHQL_QUERY, 'variables': variables}, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print(f"GraphQL Error: {data['errors']}")
            return candidates
        
        prs = data['data']['repository']['pullRequests']['nodes']
        
        for pr in prs:
            # Heuristic Filtering: Must touch `min_files` and actually reference an issue
            if pr['changedFiles'] >= min_files and len(pr['closingIssuesReferences']['nodes']) > 0:
                issues = pr['closingIssuesReferences']['nodes']
                candidates.append({
                    "pr_number": pr['number'],
                    "pr_url": pr['url'],
                    "changed_files": pr['changedFiles'],
                    "base_commit": pr['baseRefOid'],
                    "issues": [issue['number'] for issue in issues]
                })
        print(f"Found {len(candidates)} complex PR candidates touching >= {min_files} files.")
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(response.text)

    return candidates

if __name__ == "__main__":
    # Test with a known repository from our testing_list.md
    # We will test Kubernetes (Go) as a sample
    sample_owner = "kubernetes"
    sample_repo = "kubernetes"
    
    # Needs a valid .env with GITHUB_TOKEN to run successfully
    candidates = fetch_complex_prs(sample_owner, sample_repo, min_files=4)
    
    # Save output to a sample json file to review the structure
    with open("sample_candidates.json", "w") as f:
        json.dump(candidates, f, indent=4)
