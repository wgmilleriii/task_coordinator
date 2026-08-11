import os
import glob
import yaml
from flask import Flask, jsonify, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVE_DIR = os.path.join(BASE_DIR, 'tasks', 'active')

def load_tasks():
    tasks = []
    if not os.path.exists(ACTIVE_DIR):
        return tasks
        
    for filepath in glob.glob(os.path.join(ACTIVE_DIR, '*.yaml')):
        with open(filepath, 'r') as f:
            try:
                task = yaml.safe_load(f)
                if task:
                    tasks.append(task)
            except yaml.YAMLError:
                pass
    return tasks

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks')
def api_tasks():
    tasks = load_tasks()
    
    # Categorize tasks for the human
    todo = []
    review = []
    audit = []
    
    for t in tasks:
        status = t.get('status')
        lane = t.get('lane')
        
        if status == 'HUMAN_REVIEW':
            review.append(t)
        elif lane == 'HUMAN' and status in ['AUDITED', 'CLAIMED', 'IN_PROGRESS']:
            todo.append(t)
        elif status == 'OPEN':
            audit.append(t)
            
    # Sort by priority
    priority_map = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    def sort_key(task):
        return priority_map.get(task.get('priority', 'P3'), 3)
        
    todo.sort(key=sort_key)
    review.sort(key=sort_key)
    audit.sort(key=sort_key)
    
    return jsonify({
        'todo': todo,
        'review': review,
        'audit': audit,
        'all_active': len(tasks)
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
