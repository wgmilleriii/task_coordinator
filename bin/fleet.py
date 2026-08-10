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
    with open(os.path.join(ACTIVE_DIR, f"{task_id}.yaml"), 'w') as f:
        yaml.dump(task_data, f, sort_keys=False)

def cmd_lint(args):
    schema = load_schema('task')
    tasks_with_files = load_all_tasks()
    
    errors = 0
    seen_ids = set()
    
    for filename, task in tasks_with_files:
        task_id = task.get('id', 'Unknown')
        
        # 1. Check Schema Validity
        try:
            jsonschema.validate(instance=task, schema=schema, format_checker=jsonschema.FormatChecker())
        except jsonschema.exceptions.ValidationError as e:
            print(f"❌ {filename}: Schema Error - {e.message}")
            errors += 1
            continue
            
        # 2. Check for Duplicate IDs
        if task_id in seen_ids:
            print(f"❌ {filename}: Duplicate Task ID detected '{task_id}'")
            errors += 1
        seen_ids.add(task_id)
        
        # 3. Check filename alignment
        expected_filename = f"{task_id}.yaml"
        if filename != expected_filename:
            print(f"❌ {filename}: Filename does not match Task ID '{task_id}'. Expected '{expected_filename}'.")
            errors += 1
            
        # 4. Check dependencies exist
        deps = task.get('dependencies', [])
        for dep in deps:
            # We must check this after collecting all IDs, so we will do a second pass for dependencies.
            pass

    # Second pass for dependencies
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
    # Sort by repo, then priority, then status
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    tasks.sort(key=lambda x: (x.get('repo', ''), priority_order.get(x.get('priority', 'P3')), x.get('status', '')))
    
    with open(TASKS_MD, 'w') as f:
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
    print(f"✅ Rendered {TASKS_MD}")

def cmd_claim(args):
    tasks = [t[1] for t in load_all_tasks()]
    for task in tasks:
        if task['id'] == args.task_id:
            if task['status'] != 'AUDITED':
                print(f"❌ Cannot claim {args.task_id}. Status is {task['status']}, must be AUDITED.")
                return 1
            # Check for repo locks (one agent per repo)
            repo = task['repo']
            for other_task in tasks:
                if other_task['repo'] == repo and other_task['status'] in ['CLAIMED', 'IN_PROGRESS']:
                    print(f"❌ Cannot claim {args.task_id}. Repo '{repo}' is locked by {other_task['id']} ({other_task['owner']}).")
                    return 1
            
            task['status'] = 'CLAIMED'
            task['owner'] = args.owner
            save_task(task)
            print(f"✅ Successfully claimed {args.task_id} for {args.owner}.")
            cmd_render(None)
            return 0
    print(f"❌ Task {args.task_id} not found.")
    return 1

def main():
    parser = argparse.ArgumentParser(description="Dollers Fleet V2 Task Coordinator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    lint_parser = subparsers.add_parser("lint", help="Validate all active tasks against the schema")
    
    render_parser = subparsers.add_parser("render", help="Generate TASKS.md from YAML files")
    
    claim_parser = subparsers.add_parser("claim", help="Claim an AUDITED task")
    claim_parser.add_argument("task_id", help="The Task ID (e.g. T-MIN-001)")
    claim_parser.add_argument("--owner", required=True, help="Platform/Agent name claiming the task")
    
    args = parser.parse_args()
    
    if args.command == "lint":
        sys.exit(cmd_lint(args))
    elif args.command == "render":
        sys.exit(cmd_render(args))
    elif args.command == "claim":
        sys.exit(cmd_claim(args))

if __name__ == "__main__":
    main()
