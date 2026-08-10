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

    if errors == 0:
        print("✅ All tasks passed strict schema validation.")
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
            save_task(task)
            print(f"✅ Successfully claimed {args.task_id} for {args.owner}.")
            cmd_render(argparse.Namespace(quiet=True))
            return 0
    print(f"❌ Task {args.task_id} not found.")
    return 1

def cmd_submit(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
    if task['status'] not in ['CLAIMED', 'IN_PROGRESS']:
        print(f"❌ Cannot submit {args.task_id}. Status is {task['status']}, must be CLAIMED or IN_PROGRESS.")
        return 1
    
    task['status'] = 'PEER_REVIEW'
    save_task(task)
    print(f"✅ Task {args.task_id} submitted for PEER_REVIEW.")
    
    handoff = {
        "task_id": args.task_id,
        "agent": task.get('owner', 'Unknown'),
        "model": "Unknown",
        "status": "PEER_REVIEW",
        "target_repo": task.get('repo', 'Unknown'),
        "branch": "test",
        "base_sha": task.get('audited_repo_sha', 'Unknown'),
        "head_sha": "REQUIRED",
        "evidence_output": args.evidence_output
    }
    
    handoffs_dir = os.path.join(BASE_DIR, 'handoffs')
    os.makedirs(handoffs_dir, exist_ok=True)
    handoff_path = os.path.join(handoffs_dir, f"{args.task_id}_handoff.yaml")
    with open(handoff_path, 'w') as f:
        yaml.dump(handoff, f, sort_keys=False)
        
    print(f"✅ Generated handoff template at {handoff_path}")
    cmd_render(argparse.Namespace(quiet=True))
    return 0

def cmd_close(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
    if task['status'] not in ['PEER_REVIEW', 'HUMAN_REVIEW']:
        print(f"❌ Cannot close {args.task_id}. Status is {task['status']}, must be in REVIEW.")
        return 1
        
    task['status'] = 'DONE'
    save_task(task)
    print(f"✅ Task {args.task_id} successfully marked as DONE.")
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
    claim_parser.add_argument("task_id")
    claim_parser.add_argument("--owner", required=True)
    
    submit_parser = subparsers.add_parser("submit", help="Submit a CLAIMED task for review")
    submit_parser.add_argument("task_id")
    submit_parser.add_argument("--evidence-output", required=True)
    
    close_parser = subparsers.add_parser("close", help="Mark a REVIEW task as DONE")
    close_parser.add_argument("task_id")
    
    args = parser.parse_args()
    
    if args.command == "lint":
        sys.exit(cmd_lint(args))
    elif args.command == "render":
        sys.exit(cmd_render(args))
    elif args.command == "audit":
        sys.exit(cmd_audit(args))
    elif args.command == "claim":
        sys.exit(cmd_claim(args))
    elif args.command == "submit":
        sys.exit(cmd_submit(args))
    elif args.command == "close":
        sys.exit(cmd_close(args))

if __name__ == "__main__":
    main()
