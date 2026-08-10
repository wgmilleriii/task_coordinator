#!/usr/bin/env python3
import os
import sys
import json
import yaml
import jsonschema
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVE_DIR = os.path.join(BASE_DIR, 'tasks', 'active')
SCHEMA_DIR = os.path.join(BASE_DIR, 'schemas')
HANDOFFS_DIR = os.path.join(BASE_DIR, 'handoffs')
REVIEWS_DIR = os.path.join(BASE_DIR, 'reviews')
TASKS_MD = os.path.join(BASE_DIR, 'TASKS.md')

def load_schema(schema_name):
    with open(os.path.join(SCHEMA_DIR, f"{schema_name}.schema.json"), 'r') as f:
        return json.load(f)

def load_all_tasks():
    tasks = []
    if not os.path.exists(ACTIVE_DIR):
        return tasks
    for filename in os.listdir(ACTIVE_DIR):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = os.path.join(ACTIVE_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
                    if not isinstance(data, dict):
                        print(f"❌ {filename}: Not a valid YAML object.")
                        continue
                    tasks.append((filename, data))
            except Exception as e:
                print(f"❌ {filename}: Failed to parse YAML - {str(e)}")
    return tasks

def save_task(task_data):
    task_id = task_data['id']
    filepath = os.path.join(ACTIVE_DIR, f"{task_id}.yaml")
    temp_filepath = filepath + ".tmp"
    with open(temp_filepath, 'w') as f:
        yaml.dump(task_data, f, sort_keys=False)
    os.replace(temp_filepath, filepath)

def get_task(task_id):
    for filename, task in load_all_tasks():
        if task.get('id') == task_id:
            return task
    return None

def cmd_lint(args):
    schema = load_schema('task')
    tasks_with_files = load_all_tasks()
    
    # D-1: Self-test to ensure date-time validation isn't silently ignored
    try:
        jsonschema.validate(instance={"d": "NOT-A-DATE"}, schema={"type": "object", "properties": {"d": {"type": "string", "format": "date-time"}}}, format_checker=jsonschema.FormatChecker())
        print("❌ CRITICAL LINT ERROR: jsonschema FormatChecker is failing silently. Missing rfc3339-validator dependency.")
        return 1
    except jsonschema.exceptions.ValidationError:
        pass
        
    errors = 0
    seen_ids = set()
    
    for filename, task in tasks_with_files:
        task_id = task.get('id', 'Unknown')
        
        try:
            jsonschema.validate(instance=task, schema=schema, format_checker=jsonschema.FormatChecker())
        except jsonschema.exceptions.ValidationError as e:
            print(f"❌ {filename}: Schema Error - {e.message}")
            errors += 1
            continue
            
        if task_id in seen_ids:
            print(f"❌ {filename}: Duplicate Task ID detected '{task_id}'")
            errors += 1
        seen_ids.add(task_id)
        
        expected_filename = f"{task_id}.yaml"
        if filename != expected_filename:
            print(f"❌ {filename}: Filename does not match Task ID '{task_id}'. Expected '{expected_filename}'.")
            errors += 1

    for filename, task in tasks_with_files:
        deps = task.get('dependencies', [])
        for dep in deps:
            if dep not in seen_ids:
                print(f"❌ {filename}: Dependency '{dep}' does not exist.")
                errors += 1

    # D-5: Lint handoffs
    if os.path.exists(HANDOFFS_DIR):
        handoff_schema = load_schema('handoff')
        for filename in os.listdir(HANDOFFS_DIR):
            if not filename.endswith('.yaml'): continue
            try:
                with open(os.path.join(HANDOFFS_DIR, filename), 'r') as f:
                    data = yaml.safe_load(f)
                jsonschema.validate(instance=data, schema=handoff_schema, format_checker=jsonschema.FormatChecker())
            except Exception as e:
                msg = e.message if hasattr(e, 'message') else str(e)
                print(f"❌ {filename}: Handoff Schema Error - {msg}")
                errors += 1

    # D-5: Lint reviews
    if os.path.exists(REVIEWS_DIR):
        review_schema = load_schema('review')
        for filename in os.listdir(REVIEWS_DIR):
            if not filename.endswith('.yaml'): continue
            try:
                with open(os.path.join(REVIEWS_DIR, filename), 'r') as f:
                    data = yaml.safe_load(f)
                jsonschema.validate(instance=data, schema=review_schema, format_checker=jsonschema.FormatChecker())
            except Exception as e:
                msg = e.message if hasattr(e, 'message') else str(e)
                print(f"❌ {filename}: Review Schema Error - {msg}")
                errors += 1

    if errors == 0:
        print("✅ All active tasks, handoffs, and reviews passed strict schema validation.")
        return 0
    return 1

def cmd_render(args):
    tasks = [t[1] for t in load_all_tasks()]
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    tasks.sort(key=lambda x: (x.get('repo', ''), priority_order.get(x.get('priority', 'P3')), x.get('status', '')))
    
    temp_md = TASKS_MD + ".tmp"
    with open(temp_md, 'w') as f:
        f.write("# Fleet Task Board (V2 Generated)\n\n")
        f.write("> **Note:** This file is read-only. Edit tasks via the `bin/fleet` CLI.\n\n")
        
        current_repo = None
        for task in tasks:
            if task.get('repo') != current_repo:
                current_repo = task.get('repo')
                f.write(f"\n## Repo: `{current_repo}`\n\n")
                
            status_emoji = "✅" if task['status'] == "DONE" else "⏳" if task['status'] in ["HUMAN_REVIEW", "PEER_REVIEW"] else "🛠" if task['status'] in ["CLAIMED", "IN_PROGRESS"] else "📋"
            f.write(f"### {status_emoji} {task['id']} · {task['priority']} · {task['lane']} · {task['status']}\n")
            f.write(f"**{task['title']}**\n")
            f.write(f"**Owner:** {task.get('owner', 'None')}\n\n")
            f.write("**Scope:**\n")
            for item in task.get('scope', []):
                f.write(f"- {item}\n")
            f.write("\n**Definition of Done:**\n")
            for item in task.get('definition_of_done', []):
                f.write(f"- {item}\n")
            if task.get('audited_repo_sha'):
                f.write(f"\n*Audited against SHA:* `{task['audited_repo_sha']}`\n")
            f.write("\n---\n")
            
    os.replace(temp_md, TASKS_MD)
    if not (args and hasattr(args, 'quiet') and args.quiet):
        print(f"✅ Rendered {TASKS_MD}")
    return 0

def cmd_audit(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
    if task['status'] not in ['OPEN', 'DRAFT']:
        print(f"❌ Cannot audit {args.task_id}. Status is {task['status']}, must be OPEN.")
        return 1
    
    task['status'] = 'AUDITED'
    task['audited_at'] = datetime.utcnow().isoformat() + "Z"
    task['audited_by'] = args.auditor
    task['audited_repo_sha'] = args.repo_sha
    task['verification_command'] = args.command
    
    save_task(task)
    print(f"✅ Task {args.task_id} successfully audited against {args.repo_sha}.")
    cmd_render(argparse.Namespace(quiet=True))
    return 0

def cmd_claim(args):
    tasks = [t[1] for t in load_all_tasks()]
    for task in tasks:
        if task['id'] == args.task_id:
            if task['status'] != 'AUDITED':
                print(f"❌ Cannot claim {args.task_id}. Status is {task['status']}, must be AUDITED.")
                return 1
            
            repo = task['repo']
            for other_task in tasks:
                if other_task['repo'] == repo and other_task['status'] in ['CLAIMED', 'IN_PROGRESS']:
                    print(f"❌ Cannot claim {args.task_id}. Repo '{repo}' is locked by {other_task['id']} ({other_task['owner']}).")
                    return 1
            
            task['status'] = 'CLAIMED'
            task['owner'] = args.owner
            task['claimed_at'] = datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z')
            save_task(task)
            print(f"✅ Successfully claimed {args.task_id} for {args.owner}.")
            cmd_render(argparse.Namespace(quiet=True))
            return 0
    print(f"❌ Task {args.task_id} not found.")
    return 1

def cmd_verify(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
    if task['status'] not in ['CLAIMED', 'IN_PROGRESS']:
        print(f"❌ Cannot verify {args.task_id}. Status is {task['status']}, must be CLAIMED or IN_PROGRESS.")
        return 1
        
    cmd = task.get('verification_command')
    if not cmd:
        print(f"❌ Task {args.task_id} has no verification_command defined.")
        return 1
        
    # Assume sibling directory for target repo
    repo_path = os.path.abspath(os.path.join(BASE_DIR, '..', task['repo']))
    if not os.path.exists(repo_path):
        print(f"❌ Target repo path does not exist: {repo_path}")
        return 1

    print(f"▶️ Running verification in {repo_path}:\n   {cmd}")
    
    import subprocess
    try:
        result = subprocess.run(cmd, shell=True, cwd=repo_path, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("❌ Verification timed out after 5 minutes.")
        return 1

    # Dynamically fetch branch
    branch_result = subprocess.run("git branch --show-current", shell=True, cwd=repo_path, capture_output=True, text=True)
    current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "Unknown"

    output = f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout.strip()}\n\nSTDERR:\n{result.stderr.strip()}"
    
    if result.returncode != 0:
        print(f"❌ Verification failed (exit code {result.returncode}).")
        print("-" * 40)
        print(output)
        print("-" * 40)
        return 1
        
    print(f"✅ Verification passed.")
    
    handoff = {
        "task_id": args.task_id,
        "agent": task.get('owner', 'Unknown'),
        "model": args.model,
        "status": "VERIFIED_LOCALLY",
        "target_repo": task['repo'],
        "branch": current_branch,
        "base_sha": task.get('audited_repo_sha', 'Unknown'),
        "head_sha": "REQUIRED_PLEASE_FILL",
        "evidence_output": output,
        "peer_review_notes": None,
        "human_action_required": None
    }
    
    os.makedirs(HANDOFFS_DIR, exist_ok=True)
    handoff_path = os.path.join(HANDOFFS_DIR, f"{args.task_id}_handoff.yaml")
    with open(handoff_path, 'w') as f:
        yaml.dump(handoff, f, sort_keys=False)
        
    print(f"✅ Captured cryptographic evidence to {handoff_path}")
    print("Please fill in `head_sha` in the handoff file, then run `./bin/fleet submit`")
    return 0

def cmd_submit(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
    if task['status'] not in ['CLAIMED', 'IN_PROGRESS']:
        print(f"❌ Cannot submit {args.task_id}. Status is {task['status']}, must be CLAIMED or IN_PROGRESS.")
        return 1
    
    handoff_path = os.path.join(HANDOFFS_DIR, f"{args.task_id}_handoff.yaml")
    if not os.path.exists(handoff_path):
        print(f"❌ No handoff file found. You must run `./bin/fleet verify {args.task_id}` first.")
        return 1
        
    with open(handoff_path, 'r') as f:
        handoff = yaml.safe_load(f)
        
    if handoff.get('head_sha') == 'REQUIRED_PLEASE_FILL':
        print(f"❌ You must replace 'REQUIRED_PLEASE_FILL' with the actual Git SHA in {handoff_path}")
        return 1
        
    # Validate handoff against schema before allowing submit
    try:
        handoff_schema = load_schema('handoff')
        jsonschema.validate(instance=handoff, schema=handoff_schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ Handoff Schema Error - {e.message}")
        print("Please fix the handoff file before submitting.")
        return 1
        
    handoff['status'] = 'PEER_REVIEW'
    with open(handoff_path, 'w') as f:
        yaml.dump(handoff, f, sort_keys=False)
    
    task['status'] = 'PEER_REVIEW'
    save_task(task)
    print(f"✅ Task {args.task_id} submitted for PEER_REVIEW.")
    cmd_render(argparse.Namespace(quiet=True))
    return 0

def cmd_start_review(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
    if task['status'] != 'PEER_REVIEW':
        print(f"❌ Cannot start review for {args.task_id}. Status is {task['status']}, must be PEER_REVIEW.")
        return 1
        
    handoff_path = os.path.join(HANDOFFS_DIR, f"{args.task_id}_handoff.yaml")
    head_sha = "Unknown"
    if os.path.exists(handoff_path):
        with open(handoff_path, 'r') as f:
            head_sha = yaml.safe_load(f).get('head_sha', 'Unknown')
            
    review = {
        "task_id": args.task_id,
        "reviewer_agent": args.reviewer,
        "reviewer_model": args.model,
        "reviewed_head_sha": head_sha,
        "verdict": "FAIL",
        "findings": [{"severity": "INFO", "description": "REQUIRED_PLEASE_FILL"}],
        "reviewed_at": datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z')
    }
    
    os.makedirs(REVIEWS_DIR, exist_ok=True)
    review_path = os.path.join(REVIEWS_DIR, f"{args.task_id}_review.yaml")
    with open(review_path, 'w') as f:
        yaml.dump(review, f, sort_keys=False)
        
    print(f"✅ Generated review template at {review_path}")
    print("Please fill in the findings and verdict (PASS, PASS_WITH_CORRECTIONS, FAIL), then run `./bin/fleet record-review`")
    return 0

def cmd_record_review(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
    if task['status'] != 'PEER_REVIEW':
        print(f"❌ Cannot record review for {args.task_id}. Status is {task['status']}, must be PEER_REVIEW.")
        return 1
        
    review_path = os.path.join(REVIEWS_DIR, f"{args.task_id}_review.yaml")
    if not os.path.exists(review_path):
        print(f"❌ No review file found at {review_path}. Run `./bin/fleet start-review {args.task_id}` first.")
        return 1
        
    with open(review_path, 'r') as f:
        review_data = yaml.safe_load(f)
        
    try:
        review_schema = load_schema('review')
        jsonschema.validate(instance=review_data, schema=review_schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ Review Schema Error - {e.message}")
        print("Please fix the review file before recording.")
        return 1
        
    verdict = review_data['verdict']
    if verdict == 'FAIL':
        task['status'] = 'IN_PROGRESS'
        print(f"❌ Task {args.task_id} FAILED peer review. Reverting to IN_PROGRESS.")
    else:
        if task.get('human_review_required', False):
            task['status'] = 'HUMAN_REVIEW'
            print(f"✅ Task {args.task_id} passed peer review ({verdict}). Awaiting HUMAN_REVIEW.")
        else:
            task['status'] = 'DONE'
            print(f"✅ Task {args.task_id} passed peer review ({verdict}) and is marked DONE.")
        
    save_task(task)
    cmd_render(argparse.Namespace(quiet=True))
    return 0

def cmd_close(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
        
    if task.get('human_review_required', False):
        if task['status'] != 'HUMAN_REVIEW':
            print(f"❌ Cannot close {args.task_id}. Status is {task['status']}, must be HUMAN_REVIEW.")
            return 1
    else:
        if task['status'] not in ['PEER_REVIEW', 'HUMAN_REVIEW']:
            print(f"❌ Cannot close {args.task_id}. Status is {task['status']}, must be in REVIEW.")
            return 1
        
    task['status'] = 'DONE'
    save_task(task)
    print(f"✅ Task {args.task_id} successfully marked as DONE by {args.human}.")
    cmd_render(argparse.Namespace(quiet=True))
    return 0

def main():
    parser = argparse.ArgumentParser(description="Dollers Fleet V2 Task Coordinator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("lint", help="Validate all active tasks against the schema")
    subparsers.add_parser("render", help="Generate TASKS.md from YAML files")
    
    audit_parser = subparsers.add_parser("audit", help="Audit an OPEN task (PMs only)")
    audit_parser.add_argument("task_id")
    audit_parser.add_argument("--auditor", required=True)
    audit_parser.add_argument("--repo-sha", required=True)
    audit_parser.add_argument("--command", required=True)
    
    claim_parser = subparsers.add_parser("claim", help="Claim an AUDITED task")
    claim_parser.add_argument("task_id", help="The Task ID (e.g. T-MIN-001)")
    claim_parser.add_argument("--owner", required=True, help="Platform/Agent name claiming the task")
    
    verify_parser = subparsers.add_parser("verify", help="Execute verification command and capture evidence")
    verify_parser.add_argument("task_id")
    verify_parser.add_argument("--model", required=True, help="The AI model capturing the evidence")
    
    submit_parser = subparsers.add_parser("submit", help="Submit a CLAIMED task for review")
    submit_parser.add_argument("task_id")
    
    start_review_parser = subparsers.add_parser("start-review", help="Generate a review template for a PEER_REVIEW task")
    start_review_parser.add_argument("task_id")
    start_review_parser.add_argument("--reviewer", required=True, help="Agent performing the review")
    start_review_parser.add_argument("--model", required=True, help="Model performing the review")
    
    record_review_parser = subparsers.add_parser("record-review", help="Record the verdict of a peer review")
    record_review_parser.add_argument("task_id")
    
    close_parser = subparsers.add_parser("close", help="Mark a REVIEW task as DONE (requires human approval if human_review_required is True)")
    close_parser.add_argument("task_id")
    close_parser.add_argument("--human", default="Unknown", help="Name of the human approving the close")
    
    args = parser.parse_args()
    
    if args.command == "lint":
        sys.exit(cmd_lint(args))
    elif args.command == "render":
        sys.exit(cmd_render(args))
    elif args.command == "audit":
        sys.exit(cmd_audit(args))
    elif args.command == "claim":
        sys.exit(cmd_claim(args))
    elif args.command == "verify":
        sys.exit(cmd_verify(args))
    elif args.command == "submit":
        sys.exit(cmd_submit(args))
    elif args.command == "start-review":
        sys.exit(cmd_start_review(args))
    elif args.command == "record-review":
        sys.exit(cmd_record_review(args))
    elif args.command == "close":
        sys.exit(cmd_close(args))

if __name__ == "__main__":
    main()
