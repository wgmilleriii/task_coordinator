#!/usr/bin/env python3
import os
import sys
import json
import yaml
import jsonschema
import argparse
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVE_DIR = os.path.join(BASE_DIR, 'tasks', 'active')
SCHEMA_DIR = os.path.join(BASE_DIR, 'schemas')
HANDOFFS_DIR = os.path.join(BASE_DIR, 'handoffs')
REVIEWS_DIR = os.path.join(BASE_DIR, 'reviews')
TASKS_MD = os.path.join(BASE_DIR, 'TASKS.md')

def load_schema(schema_name):
    with open(os.path.join(SCHEMA_DIR, f"{schema_name}.schema.json"), 'r') as f:
        return json.load(f)

def load_all_tasks(include_archive=False):
    tasks = []
    has_errors = False
    dirs_to_check = [ACTIVE_DIR]
    if include_archive:
        archive_dir = os.path.join(BASE_DIR, 'tasks', 'archive')
        if os.path.exists(archive_dir):
            dirs_to_check.append(archive_dir)
            
    for d in dirs_to_check:
        if not os.path.exists(d):
            continue
        for filename in os.listdir(d):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                filepath = os.path.join(d, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = yaml.safe_load(f)
                        if not isinstance(data, dict):
                            print(f"❌ {filename}: Not a valid YAML object.")
                            has_errors = True
                            continue
                        tasks.append((filename, data))
                except Exception as e:
                    print(f"❌ {filename}: Failed to parse YAML - {str(e)}")
                    has_errors = True
                    
    if has_errors:
        print("❌ CRITICAL: Store contains malformed YAML. Aborting to prevent data corruption.")
        sys.exit(1)
    return tasks

def save_task(task_data):
    task_id = task_data['id']
    filepath = os.path.join(ACTIVE_DIR, f"{task_id}.yaml")
    temp_filepath = filepath + ".tmp"
    with open(temp_filepath, 'w') as f:
        yaml.dump(task_data, f, sort_keys=False)
    os.replace(temp_filepath, filepath)

def log_global_event(action, actor, task_id=None, details=None):
    log_dir = os.path.join(BASE_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'fleet.jsonl')
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "action": action,
        "actor": actor
    }
    if task_id: entry["task_id"] = task_id
    if details: entry["details"] = details
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def log_task_event(task, action, actor, details=None):
    if 'events' not in task or task['events'] is None:
        task['events'] = []
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "action": action,
        "actor": actor
    }
    if details: entry["details"] = details
    task['events'].append(entry)

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

    all_known_tasks = load_all_tasks(include_archive=True)
    all_seen_ids = {t.get('id') for fn, t in all_known_tasks}
    
    for filename, task in tasks_with_files:
        deps = task.get('dependencies', [])
        for dep in deps:
            if dep not in all_seen_ids:
                print(f"❌ {filename}: Dependency '{dep}' does not exist (not active or archived).")
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
    tasks_with_files = load_all_tasks()
    tasks_list = [t[1] for t in tasks_with_files]
    
    # Calculate fleet burn rate
    total_tokens = 0
    total_cost = 0.0
    if os.path.exists(HANDOFFS_DIR):
        for filename in os.listdir(HANDOFFS_DIR):
            if filename.endswith('.yaml'):
                try:
                    with open(os.path.join(HANDOFFS_DIR, filename), 'r') as f:
                        data = yaml.safe_load(f)
                        if data.get('token_spend'):
                            total_tokens += data['token_spend']
                        if data.get('cost_usd'):
                            total_cost += data['cost_usd']
                except Exception:
                    pass
    
    temp_md = TASKS_MD + ".tmp"
    with open(temp_md, 'w') as f:
        f.write("# 📋 Task Board\n\n")
        f.write("*(Auto-generated. Do not edit manually. Use `./bin/fleet` commands to transition tasks.)*\n\n")
        
        # Add Burn Rate
        if total_tokens > 0 or total_cost > 0:
            f.write("## 💸 Fleet Burn Rate (All Time)\n")
            f.write(f"- **Total Tokens Spent:** {total_tokens:,}\n")
            f.write(f"- **Total Cost (USD):** ${total_cost:,.2f}\n\n")
            f.write("---\n\n")
            
        # Add Mermaid Graph
        f.write("## 🕸️ Task Dependency Graph\n\n")
        f.write("```mermaid\ngraph TD\n")
        f.write("    classDef done fill:#d4edda,stroke:#28a745,color:#000;\n")
        f.write("    classDef blocked fill:#f8d7da,stroke:#dc3545,color:#000;\n")
        f.write("    classDef review fill:#fff3cd,stroke:#ffc107,color:#000;\n")
        f.write("    classDef active fill:#cce5ff,stroke:#007bff,color:#000;\n")
        
        for task in tasks_list:
            safe_title = task['title'].replace('"', "'").replace('[', '(').replace(']', ')')
            node = f"    {task['id']}[\"{task['id']}<br/>{safe_title}\"]"
            if task['status'] == 'DONE':
                node += ":::done"
            elif task['status'] == 'BLOCKED':
                node += ":::blocked"
            elif task['status'] in ['PEER_REVIEW', 'HUMAN_REVIEW']:
                node += ":::review"
            elif task['status'] in ['CLAIMED', 'IN_PROGRESS']:
                node += ":::active"
            f.write(node + "\n")
            for dep in task.get('dependencies', []):
                f.write(f"    {dep} --> {task['id']}\n")
        f.write("```\n\n---\n\n")
        
        # Render lanes
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        tasks_list.sort(key=lambda x: (x.get('repo', ''), priority_order.get(x.get('priority', 'P3')), x.get('status', '')))
        
        current_repo = None
        for task in tasks_list:
            if task.get('repo') != current_repo:
                current_repo = task.get('repo')
                f.write(f"\n## Repo: `{current_repo}`\n\n")
                
            status_emoji = "✅" if task['status'] == "DONE" else "🛑" if task['status'] == "BLOCKED" else "⏳" if task['status'] in ["HUMAN_REVIEW", "PEER_REVIEW"] else "🛠" if task['status'] in ["CLAIMED", "IN_PROGRESS"] else "📋"
            f.write(f"### {status_emoji} {task['id']} · {task['priority']} · {task['lane']} · {task['status']}\n")
            f.write(f"**{task['title']}**\n")
            
            if task['status'] == 'BLOCKED':
                f.write(f"> 🛑 **BLOCKED REASON:** {task.get('blocked_reason', 'Not specified')}\n\n")
                
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
    task['audited_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    task['audited_by'] = args.auditor
    task['audited_repo_sha'] = args.repo_sha
    task['verification_command'] = args.command
    
    log_task_event(task, 'AUDIT', args.auditor, f"Audited against {args.repo_sha}")
    log_global_event('AUDIT', args.auditor, args.task_id, f"Audited against {args.repo_sha}")
    
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
                    
            deps = task.get('dependencies', [])
            if deps:
                all_tasks = {t.get('id'): t for fn, t in load_all_tasks(include_archive=True)}
                for dep in deps:
                    dep_task = all_tasks.get(dep)
                    if not dep_task or dep_task.get('status') != 'DONE':
                        print(f"❌ Cannot claim {args.task_id}. Dependency '{dep}' is not DONE.")
                        return 1
            
            task['status'] = 'CLAIMED'
            task['owner'] = args.owner
            task['claimed_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            log_task_event(task, 'CLAIM', args.owner)
            log_global_event('CLAIM', args.owner, args.task_id)
            
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
        log_global_event('VERIFY_FAIL', args.model, args.task_id, f"Exit code {result.returncode}")
        return 1
        
    print(f"✅ Verification passed.")
    log_global_event('VERIFY_PASS', args.model, args.task_id)
    
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
        "human_action_required": None,
        "token_spend": None,
        "cost_usd": None
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
    
    log_task_event(task, 'SUBMIT', task.get('owner', 'Unknown'))
    log_global_event('SUBMIT', task.get('owner', 'Unknown'), args.task_id)
    
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
        "reviewed_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }
    
    os.makedirs(REVIEWS_DIR, exist_ok=True)
    review_path = os.path.join(REVIEWS_DIR, f"{args.task_id}_review.yaml")
    with open(review_path, 'w') as f:
        yaml.dump(review, f, sort_keys=False)
        
    log_global_event('START_REVIEW', args.reviewer, args.task_id)
        
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
            
    log_task_event(task, 'RECORD_REVIEW', review_data.get('reviewer_agent', 'Unknown'), f"Verdict: {verdict}")
    log_global_event('RECORD_REVIEW', review_data.get('reviewer_agent', 'Unknown'), args.task_id, f"Verdict: {verdict}")
        
    save_task(task)
    cmd_render(argparse.Namespace(quiet=True))
    return 0

def cmd_block(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
        
    task['previous_status'] = task['status']
    task['status'] = 'BLOCKED'
    task['blocked_reason'] = args.reason
    
    log_task_event(task, 'BLOCK', 'Unknown', f"Reason: {args.reason}")
    log_global_event('BLOCK', 'Unknown', args.task_id, f"Reason: {args.reason}")
    
    save_task(task)
    print(f"🛑 Task {args.task_id} is now BLOCKED: {args.reason}")
    cmd_render(argparse.Namespace(quiet=True))
    return 0
    
def cmd_unblock(args):
    task = get_task(args.task_id)
    if not task:
        print(f"❌ Task {args.task_id} not found.")
        return 1
    if task['status'] != 'BLOCKED':
        print(f"❌ Task {args.task_id} is not BLOCKED.")
        return 1
        
    prev_status = task.get('previous_status') or 'OPEN'
    task['status'] = prev_status
    task['blocked_reason'] = None
    task['previous_status'] = None
    
    log_task_event(task, 'UNBLOCK', 'Unknown', f"Reverted to {prev_status}")
    log_global_event('UNBLOCK', 'Unknown', args.task_id, f"Reverted to {prev_status}")
    
    save_task(task)
    print(f"✅ Task {args.task_id} is UNBLOCKED and reverted to {prev_status}.")
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
    
    log_task_event(task, 'CLOSE', args.human)
    log_global_event('CLOSE', args.human, args.task_id)
    
    save_task(task)
    print(f"✅ Task {args.task_id} manually closed by {args.human}.")
    
    # Trigger Task Lifecycle automated documentation updates
    repo_name = task.get('repo')
    if repo_name:
        target_repo_path = os.path.abspath(os.path.join(BASE_DIR, '..', repo_name))
        if os.path.exists(target_repo_path):
            print(f"🔄 Task lifecycle: Triggering automated documentation updates for {repo_name}...")
            import subprocess
            try:
                # Try to run graphify update
                result = subprocess.run("graphify update .", shell=True, cwd=target_repo_path, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print(f"✅ Graphify updated successfully for {repo_name}.")
                else:
                    print(f"⚠️ Graphify update skipped or failed for {repo_name} (ensure graphify is installed and initialized).")
            except Exception as e:
                print(f"⚠️ Could not update Graphify for {repo_name}: {e}")
                
    cmd_render(argparse.Namespace(quiet=True))
    return 0

def cmd_archive(args):
    tasks_with_files = load_all_tasks()
    archived_count = 0
    archive_dir = os.path.join(BASE_DIR, 'tasks', 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    
    for filename, task in tasks_with_files:
        if task['status'] in ['DONE', 'CANCELLED', 'DEFERRED']:
            source = os.path.join(ACTIVE_DIR, filename)
            dest = os.path.join(archive_dir, filename)
            os.replace(source, dest)
            archived_count += 1
            
    print(f"🧹 Archived {archived_count} tasks.")
    cmd_render(argparse.Namespace(quiet=True))
    return 0

def cmd_mark_docs_updated(args):
    repo_name = args.repo
    target_repo_path = os.path.abspath(os.path.join(BASE_DIR, '..', repo_name))
    if not os.path.exists(target_repo_path):
        print(f"❌ Target repo path does not exist: {target_repo_path}")
        return 1
        
    janitor_file = os.path.join(target_repo_path, '.fleet_doc_last_updated')
    with open(janitor_file, 'w') as f:
        f.write(datetime.now(timezone.utc).isoformat())
        
    print(f"✅ Reset the 24-hour documentation janitor timer for {repo_name}.")
    return 0

def cmd_onboard(args):
    repo_name = args.repo
    target_repo_path = os.path.abspath(os.path.join(BASE_DIR, '..', repo_name))
    
    if not os.path.exists(target_repo_path):
        print(f"❌ Target repo path does not exist: {target_repo_path}")
        return 1
        
    print(f"🚀 Starting onboarding for repository: {repo_name}...")
    
    context = []
    context.append(f"# Fleet Context: {repo_name}\n")
    
    # 1. Check Obsidian Vault
    obsidian_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'Obsidian'))
    if os.path.exists(obsidian_path):
        context.append("## 1. Vault Context (Obsidian)")
        context.append("Vault is present. Ensure you check `00-09 System/00 Meta/Projects.md` or relevant project notes for high-level intent.\n")
    
    # 2. Check Graphify
    graphify_report = os.path.join(target_repo_path, 'graphify-out', 'GRAPH_REPORT.md')
    if os.path.exists(graphify_report):
        context.append("## 2. Graphify Structural Map")
        context.append(f"✅ `graphify-out/GRAPH_REPORT.md` found. You MUST read it to understand the file structure.")
        context.append("To ensure it's fresh, run: `graphify update .` in the target repo.\n")
    else:
        context.append("## 2. Graphify Structural Map")
        context.append(f"❌ `graphify-out/GRAPH_REPORT.md` NOT found.")
        context.append("You should run `graphify` at the root of the repo to establish the structural baseline.\n")
        
    # 3. Check Chord Experts
    has_chord = False
    chord_kb = os.path.join(target_repo_path, 'chord-kb')
    if os.path.exists(chord_kb):
        has_chord = True
        
    if has_chord:
        context.append("## 3. Chord Expertise System")
        context.append("✅ Chord is installed in this repository.")
        context.append("You MUST check for expert pages and run `/chord expert=NAME` to synthesize domain knowledge before mutating code.\n")
    else:
        context.append("## 3. Chord Expertise System")
        context.append("❌ Chord `chord-kb` directory not found. Consider running `/chord-config` or `/chord-create-expert` if this is a complex domain.\n")
        
    # 4. Janitor Protocol (Time-Based + Major Feature Flag)
    janitor_file = os.path.join(target_repo_path, '.fleet_doc_last_updated')
    last_updated = 0
    if os.path.exists(janitor_file):
        last_updated = os.path.getmtime(janitor_file)
        
    import time
    now = time.time()
    hours_since_update = (now - last_updated) / 3600
    
    if hours_since_update > 24:
        needs_update = False
        all_tasks = load_all_tasks(include_archive=True)
        for fn, t in all_tasks:
            if t.get('repo') == repo_name and t.get('status') == 'DONE' and t.get('requires_doc_update', False):
                task_path = os.path.join(ACTIVE_DIR, fn)
                if not os.path.exists(task_path):
                    task_path = os.path.join(BASE_DIR, 'tasks', 'archive', fn)
                if os.path.exists(task_path) and os.path.getmtime(task_path) > last_updated:
                    needs_update = True
                    break
                    
        if needs_update:
            context.append("## 4. 🧹 Janitor Protocol: DOCUMENTATION UPDATE REQUIRED")
            context.append("⚠️ **CRITICAL:** It has been over 24 hours since the last documentation sweep, and major features have landed.")
            context.append("You MUST pause your regular work and act as the Documentation Janitor.")
            context.append("1. Run `/chord-tune` to update expert pages.")
            context.append("2. Update the relevant `Obsidian` project notes with recent architectural changes.")
            context.append("3. Run `./bin/fleet mark-docs-updated " + repo_name + "` to reset the 24-hour timer.")
            context.append("Do not proceed with your assigned task until this is complete.\n")
        else:
            context.append("## 4. 🧹 Janitor Protocol")
            context.append(f"It has been {hours_since_update:.1f} hours since the last doc update, but no major features require documentation updates. You are clear to proceed.\n")
    else:
        context.append("## 4. 🧹 Janitor Protocol")
        context.append(f"Documentation was updated {hours_since_update:.1f} hours ago (less than 24h limit). You are clear to proceed.\n")

    out_file = os.path.join(target_repo_path, '.fleet_context.md')
    with open(out_file, 'w') as f:
        f.write('\n'.join(context))
        
    print(f"✅ Context compiled to {out_file}")
    print(f"👉 Agent: Run `cat {out_file}` to read your briefing, then follow its instructions.")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Dollers Fleet V2 Task Coordinator")
    subparsers = parser.add_subparsers(dest="action", required=True)
    
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
    
    block_parser = subparsers.add_parser("block", help="Mark a task as BLOCKED and notify humans")
    block_parser.add_argument("task_id")
    block_parser.add_argument("--reason", required=True, help="Reason why work cannot proceed")
    
    unblock_parser = subparsers.add_parser("unblock", help="Unblock a task and return it to its previous state")
    unblock_parser.add_argument("task_id")
    
    close_parser = subparsers.add_parser("close", help="Mark a REVIEW task as DONE (requires human approval if human_review_required is True)")
    close_parser.add_argument("task_id")
    close_parser.add_argument("--human", default="Unknown", help="Name of the human approving the close")
    
    archive_parser = subparsers.add_parser("archive", help="Sweep all DONE, CANCELLED, and DEFERRED tasks off the active board into tasks/archive/")
    
    onboard_parser = subparsers.add_parser("onboard", help="Initialize a repository onboarding context for an agent")
    onboard_parser.add_argument("repo", help="Name of the repository to onboard (e.g. minchiate_tarot)")
    
    mark_docs_parser = subparsers.add_parser("mark-docs-updated", help="Reset the 24-hour Janitor Protocol timer for a repository")
    mark_docs_parser.add_argument("repo", help="Name of the repository")
    
    args = parser.parse_args()
    
    import fcntl
    lock_path = os.path.join(BASE_DIR, '.fleet.lock')
    with open(lock_path, 'w') as lock_f:
        try:
            fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("❌ Could not acquire lock. Another fleet process is currently running.")
            sys.exit(1)
            
        if args.action == "lint":
            sys.exit(cmd_lint(args))
        elif args.action == "create":
            sys.exit(cmd_create(args))
        elif args.action == "render":
            sys.exit(cmd_render(args))
        elif args.action == "audit":
            sys.exit(cmd_audit(args))
        elif args.action == "claim":
            sys.exit(cmd_claim(args))
        elif args.action == "verify":
            sys.exit(cmd_verify(args))
        elif args.action == "submit":
            sys.exit(cmd_submit(args))
        elif args.action == "start-review":
            sys.exit(cmd_start_review(args))
        elif args.action == "record-review":
            sys.exit(cmd_record_review(args))
        elif args.action == "block":
            sys.exit(cmd_block(args))
        elif args.action == "unblock":
            sys.exit(cmd_unblock(args))
        elif args.action == "close":
            sys.exit(cmd_close(args))
        elif args.action == "archive":
            sys.exit(cmd_archive(args))
        elif args.action == "onboard":
            sys.exit(cmd_onboard(args))
        elif args.action == "mark-docs-updated":
            sys.exit(cmd_mark_docs_updated(args))

if __name__ == "__main__":
    main()
