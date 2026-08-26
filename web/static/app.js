document.addEventListener('DOMContentLoaded', () => {
    fetchTasks();
});

async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        
        document.getElementById('activeCount').textContent = data.all_active;
        
        renderList('todoList', 'todoCount', data.todo, "You're all caught up! No tasks in the HUMAN lane.");
        renderList('reviewList', 'reviewCount', data.review, "No tasks awaiting your review right now.");
        renderList('auditList', 'auditCount', data.audit, "No new tasks need auditing.");
        
    } catch (error) {
        console.error("Error fetching tasks:", error);
        document.querySelectorAll('.task-list').forEach(list => {
            list.innerHTML = `<div class="empty-state" style="color: var(--danger)">Failed to load tasks. Ensure the Flask server is running.</div>`;
        });
    }
}

function renderList(containerId, badgeId, tasks, emptyMessage) {
    const container = document.getElementById(containerId);
    const badge = document.getElementById(badgeId);
    
    badge.textContent = tasks.length;
    container.innerHTML = '';
    
    if (tasks.length === 0) {
        container.innerHTML = `<div class="empty-state">${emptyMessage}</div>`;
        return;
    }
    
    tasks.forEach(task => {
        const card = document.createElement('div');
        card.className = 'task-card';
        
        const priorityStr = task.priority || 'P3';
        const ownerStr = task.owner ? ` • ${task.owner}` : '';
        const epicHTML = task.epic ? `<span class="task-epic" style="background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 2px 6px; font-size: 0.75rem; margin-left: 6px;">🏷️ ${escapeHTML(task.epic)}</span>` : '';
        
        card.innerHTML = `
            <div class="task-header">
                <span class="task-id">${task.id}</span>
                <span class="priority priority-${priorityStr}">${priorityStr}</span>
                ${epicHTML}
            </div>
            <h3 class="task-title">${escapeHTML(task.title)}</h3>
            <div class="task-meta">
                <span class="task-repo">${task.repo}</span>
                <span class="task-status">${task.status}${ownerStr}</span>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function escapeHTML(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
