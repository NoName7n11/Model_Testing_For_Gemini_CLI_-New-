import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def get_issue_details(owner: str, repo: str, issue_number: int):
    """Fetches the original problem statement (Issue Title and Body)."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get('title', ''), data.get('body', '')
    else:
        print(f"Failed to fetch issue {issue_number}: {response.status_code}")
        return "", ""

def get_pr_diff(owner: str, repo: str, pr_number: int):
    """Fetches the raw diff of the Pull Request."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    diff_headers = HEADERS.copy()
    diff_headers['Accept'] = 'application/vnd.github.v3.diff'
    
    response = requests.get(url, headers=diff_headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch PR diff {pr_number}: {response.status_code}")
        return ""

def separate_test_and_gold_patches(raw_diff: str):
    """
    A foundational heuristic to separate tests from the actual code fix.
    In a real-world scenario, this requires robust diff parsing (e.g., unidiff library).
    For now, we split based on whether 'test' or 'spec' is in the file path.
    """
    files = raw_diff.split('diff --git ')
    gold_patch = ""
    test_patch = ""
    
    for file_diff in files:
        if not file_diff.strip():
            continue
            
        # Re-attach the splitting string
        content = 'diff --git ' + file_diff 
        
        # Look for file paths in the diff header
        match = re.search(r'a/(.+?) b/(.+?)\n', content)
        if match:
            file_path = match.group(2).lower()
            if 'test' in file_path or 'spec' in file_path:
                test_patch += content
            else:
                gold_patch += content
                
    return gold_patch, test_patch

def build_schema_task(owner: str, repo: str, language: str, pr_data: dict, issue_number: int):
    """
    Maps the scraped data perfectly into the schema_draft.json format.
    """
    title, body = get_issue_details(owner, repo, issue_number)
    raw_diff = get_pr_diff(owner, repo, pr_data['pr_number'])
    
    gold_patch, test_patch = separate_test_and_gold_patches(raw_diff)

    task_schema = {
        "task_id": f"{repo}-issue-{issue_number}",
        "repository": {
            "name": repo,
            "owner": owner,
            "language_primary": language,
            "commit_hash_base": pr_data.get('base_commit', 'UNKNOWN')
        },
        "problem_statement": {
            "title": title,
            "description": body,
            "target_files": []  # Optional: could be populated by parsing the gold_patch file names
        },
        "evaluation_criteria": {
            "gold_patch": gold_patch,
            "test_patch": test_patch,
            "success_command": "TODO: Inject repo-specific success command (e.g., 'npm map', 'go test ./...')",
            "complexity_flags": ["multi-file", "dependency-graph-verified"] if pr_data.get('changed_files', 0) >= 4 else []
        }
    }
    return task_schema

if __name__ == "__main__":
    # Example usage: Linking the Pipeline together
    # Imagine we received this data from `github_scraper.py`
    sample_scraped_data = {
        "pr_number": 115000, # Example Kubernetes PR
        "base_commit": "abcdef1234567890",
        "changed_files": 5
    }
    
    try:
        task_json = build_schema_task("kubernetes", "kubernetes", "Go", sample_scraped_data, 114000)
        
        # Save one finished evaluation task according to our schema
        output_file = "sample_task.json"
        with open(output_file, "w") as f:
            json.dump(task_json, f, indent=4)
        print(f"Successfully generated task schema and saved to {output_file}")
        
    except Exception as e:
        print(f"Error during extraction: {e}")
