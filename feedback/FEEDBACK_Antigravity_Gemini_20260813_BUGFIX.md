# Feedback: Bug Squasher (Cartesian Product in featured.php)

## System-Level Feedback
The task coordinator handles defined tasks well, but when the user reported a bug directly, there was no predefined `T-XXX` task ID for it. I created my own worktree `test-BUG-FIX-01` to ensure I followed the isolation rule. Providing a command to automatically generate a hotfix task could be useful.

## Repository-Level Feedback
The bug was reported as "marking an answer 'good answer' also marks every response in the conversation to be good". After investigating `api/ask.php`, `journal-chat.js`, and `index.php`, I verified that the core upvote logic correctly updates only a single message in the database and the local DOM.

The true source of the bug was in `featured.php`, which joins messages together to display on the Featured Gallery. When a user upvoted an answer in a conversation that had multiple preceding user questions, the `LEFT JOIN messages user_msg` clause resulted in a Cartesian product, returning multiple rows for the same upvoted answer. As a result, the same answer was displayed multiple times on the gallery (paired with different preceding questions), creating the illusion that all responses were marked as good. 

I fixed the issue by replacing the `LEFT JOIN messages user_msg` condition with a subquery `user_msg.id = (SELECT id FROM messages WHERE conversation_id = m.conversation_id AND role = 'user' AND id < m.id ORDER BY id DESC LIMIT 1)` to explicitly pair the assistant's answer with only the immediately preceding user message.
