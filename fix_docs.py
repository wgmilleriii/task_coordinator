import os

# 1. Update README.md
readme_path = '/Users/willismiller/Documents/GitHub/task_coordinator/README.md'
with open(readme_path, 'r') as f:
    readme = f.read()

readme = readme.replace(
"""Most repositories have a `test` branch which should be used for all work. If there is no `test` branch, you must create one. Always branch off `test`:
```bash
git -C ../<repo_name> worktree add ../<repo_name>-<task_id> -b test-<TASK-ID> test
```""",
"""Most repositories have a `test` branch which should be used for all work. If there is no `test` branch, you must create one. **Do NOT create new branches (no `-b`).** Instead, create a detached worktree from `test` and push your commits directly to the `test` branch when finished:
```bash
git -C ../<repo_name> worktree add --detach ../<repo_name>-<task_id> test
# After committing: git push origin HEAD:test
```"""
)

readme = readme.replace(
"""### 3. Do the Work
Per the HARD REQUIREMENT above, create an isolated worktree for this task — do not check out a branch in the Spoke repository's primary clone. Always branch from the `test` branch (create it if it doesn't exist):
```bash
git -C ../<repo_name> worktree add ../<repo_name>-<TASK-ID> -b test-<TASK-ID> test
```""",
"""### 3. Do the Work
Per the HARD REQUIREMENT above, create an isolated worktree for this task — do not check out a branch in the Spoke repository's primary clone. **Do NOT create a new branch.** Always use a detached worktree from the `test` branch (create it if it doesn't exist):
```bash
git -C ../<repo_name> worktree add --detach ../<repo_name>-<TASK-ID> test
# After committing: git push origin HEAD:test
```"""
)

with open(readme_path, 'w') as f:
    f.write(readme)

# 2. Update AGENTS.md
agents_path = '/Users/willismiller/Documents/GitHub/task_coordinator/AGENTS.md'
with open(agents_path, 'r') as f:
    agents = f.read()

agents = agents.replace(
"""   - You must NEVER commit your code directly to the `main` branch. 
   - You must create a `test` branch.""",
"""   - You must NEVER commit your code directly to the `main` branch. 
   - All work must be done on the `test` branch. Do NOT create any new branches."""
)

with open(agents_path, 'w') as f:
    f.write(agents)

# 3. Update SKILL.md
skill_path = '/Users/willismiller/.agents/skills/bug-squasher/SKILL.md'
with open(skill_path, 'r') as f:
    skill = f.read()

skill = skill.replace(
"""- Most repositories use a `test` branch as the integration branch. If it doesn't exist, you must create it.
- **ALWAYS** branch your isolated worktree off the `test` branch:
  ```bash
  git -C ../<repo_name> worktree add ../<repo_name>-<TASK-ID> -b test-<TASK-ID> test
  ```""",
"""- Most repositories use a `test` branch as the integration branch. If it doesn't exist, you must create it.
- **Do NOT create new branches.** **ALWAYS** use a detached worktree from the `test` branch and push your commits directly to `test`:
  ```bash
  git -C ../<repo_name> worktree add --detach ../<repo_name>-<TASK-ID> test
  # After committing: git push origin HEAD:test
  ```"""
)

skill = skill.replace(
"| Isolate Work | `git -C ../repo worktree add ../repo-T-XXX -b test-T-XXX test` |",
"| Isolate Work | `git -C ../repo worktree add --detach ../repo-T-XXX test` |"
)

with open(skill_path, 'w') as f:
    f.write(skill)

print("Documentation updated successfully.")
