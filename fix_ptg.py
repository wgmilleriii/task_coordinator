with open("TASKS.md", "r") as f:
    content = f.read()

task_block = """### 📋 T-PTG-059 · medium · frontend · AUDITED
**Feature: Greet the user in JournalGPT**
**Owner:** None

**Scope:**

**Definition of Done:**

*Audited against SHA:* `148499984456a86f1d1be55b74387639df92ddce`

---

"""
content = content.replace(task_block, "")

repo_header = "## Repo: `newmexicoptg.org`\n\n"
content = content.replace(repo_header, repo_header + task_block)

with open("TASKS.md", "w") as f:
    f.write(content)
