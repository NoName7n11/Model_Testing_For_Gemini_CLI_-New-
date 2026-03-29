import os
import json
from tqdm import tqdm

# Import the modules we previously built
from github_scraper import fetch_complex_prs
from patch_extractor import build_schema_task

def run_mining_pipeline(repo_configs: list, min_files: int = 4, output_dir: str = "dataset"):
    """
    Orchestrates the entire data mining pipeline:
    1. Fetches candidate PRs based on heuristics.
    2. Extracts problem statements, test patches, and gold patches.
    3. Formats them into the schema and saves them to disk.
    """
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Starting pipeline run. Output directory: {output_dir}")
    print(f"Filtering criteria: Minimum {min_files} files touched per PR.")
    
    total_tasks_curated = 0

    for config in repo_configs:
        owner = config['owner']
        name = config['name']
        language = config['language']
        
        print(f"\n--- Processing Repository: {owner}/{name} ({language}) ---")
        
        # Step 1: Scrape candidates
        candidates = fetch_complex_prs(owner, name, min_files=min_files)
        
        if not candidates:
            print(f"No valid candidates found for {owner}/{name}. Skipping.")
            continue
            
        repo_tasks_saved = 0
        
        # Step 2: Iterate through candidates and extract patches
        # Using tqdm for a nice terminal progress bar
        for pr_data in tqdm(candidates, desc=f"Extracting tasks for {name}"):
            
            # A single PR might close multiple issues. We process each linked issue.
            for issue_number in pr_data.get('issues', []):
                try:
                    # Step 3: Build the standardized schema JSON
                    task_schema = build_schema_task(owner, name, language, pr_data, issue_number)
                    
                    # Basic validation: ensure we actually grabbed text
                    if not task_schema['problem_statement']['description']:
                        continue
                        
                    task_id = task_schema['task_id']
                    
                    # Step 4: Save to disk
                    output_file = os.path.join(output_dir, f"{task_id}.json")
                    with open(output_file, "w") as f:
                        json.dump(task_schema, f, indent=4)
                    
                    repo_tasks_saved += 1
                    total_tasks_curated += 1
                    
                except Exception as e:
                    # Log the error but continue the pipeline
                    print(f"\nError processing PR {pr_data['pr_number']} / Issue {issue_number}: {e}")
                    
        print(f"Successfully curated {repo_tasks_saved} tasks from {owner}/{name}.")

    print(f"\n==========================================")
    print(f"Pipeline Complete! Total benchmark tasks curated: {total_tasks_curated}")
    print(f"Dataset generated at: ./{output_dir}/")
    print(f"==========================================")


if __name__ == "__main__":
    # Test Configuration List based on the core priorities (Python, Go, TS)
    # This simulates passing in the list from `testing_list.md`
    target_repositories = [
        {"owner": "kubernetes", "name": "kubernetes", "language": "Go"},
        {"owner": "ansible", "name": "ansible", "language": "Python"},
        {"owner": "vercel", "name": "next.js", "language": "TypeScript"}
    ]
    
    # Run the pipeline (Requires GITHUB_TOKEN in .env)
    print("Testing pipeline logic...")
    run_mining_pipeline(target_repositories, min_files=4, output_dir="../dataset")
    # print("Pipeline integration logic assembled. Uncomment the execution block to run against live GitHub APIs.")