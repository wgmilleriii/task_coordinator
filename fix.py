import yaml
import os

# Fix T-INTY-017.yaml
task_file = 'tasks/active/T-INTY-017.yaml'
with open(task_file, 'r') as f:
    data = yaml.safe_load(f)

# Convert dod -> definition_of_done (array)
if 'dod' in data:
    dod_str = data.pop('dod')
    # split by '\n' and remove empty lines and list bullets
    dod_list = [line.strip().replace('- [ ] ', '') for line in dod_str.split('\n') if line.strip()]
    data['definition_of_done'] = dod_list

# Convert scope -> array
if 'scope' in data and isinstance(data['scope'], str):
    scope_str = data['scope']
    scope_list = [line.strip() for line in scope_str.split('\n') if line.strip()]
    data['scope'] = scope_list

with open(task_file, 'w') as f:
    yaml.dump(data, f, sort_keys=False)

# Fix bin/fleet.py
fleet_file = 'bin/fleet.py'
with open(fleet_file, 'r') as f:
    content = f.read()

old_verify = """    # Assume sibling directory for target repo
    repo_path = os.path.abspath(os.path.join(BASE_DIR, '..', task['repo']))
    if not os.path.exists(repo_path):
        print(f"❌ Target repo path does not exist: {repo_path}")
        return 1

    print(f"▶️ Running verification in {repo_path}:\\n   {cmd}")
    
    import subprocess
    try:
        result = subprocess.run(cmd, shell=True, cwd=repo_path, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("❌ Verification timed out after 5 minutes.")
        return 1

    # Dynamically fetch branch
    branch_result = subprocess.run("git branch --show-current", shell=True, cwd=repo_path, capture_output=True, text=True)"""

new_verify = """    # Assume sibling directory for target repo or worktree
    worktree_path = os.path.abspath(os.path.join(BASE_DIR, '..', f"{task['repo']}-{args.task_id}"))
    repo_path = os.path.abspath(os.path.join(BASE_DIR, '..', task['repo']))
    
    if os.path.exists(worktree_path):
        target_path = worktree_path
    elif os.path.exists(repo_path):
        target_path = repo_path
    else:
        print(f"❌ Target repo path does not exist: {repo_path} or {worktree_path}")
        return 1

    print(f"▶️ Running verification in {target_path}:\\n   {cmd}")
    
    import subprocess
    try:
        result = subprocess.run(cmd, shell=True, cwd=target_path, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("❌ Verification timed out after 5 minutes.")
        return 1

    # Dynamically fetch branch
    branch_result = subprocess.run("git branch --show-current", shell=True, cwd=target_path, capture_output=True, text=True)"""

content = content.replace(old_verify, new_verify)

with open(fleet_file, 'w') as f:
    f.write(content)
